
import hashlib
import logging
import os
import platform
import shutil
import sqlite3
import tempfile
import uuid
import zipfile

from pathlib import Path

import django

from django.conf import settings
from django.db import connection
from django.utils import timezone

from .models import Backup, BACKUP_DIRECTORY


logger = logging.getLogger(__name__)


class BackupService:
    """
    Backup SQLite database and public_html/media.

    Archive structure:
        Database/
        Media/
        Information/
    """

    KEEP_LAST_BACKUPS = 30
    COPY_CHUNK_SIZE = 1024 * 1024

    def __init__(self):
        self.project_root = Path(
            settings.BASE_DIR
        ).resolve()

        self.backup_root = Path(
            BACKUP_DIRECTORY
        ).resolve()

        self.temp_root = (
            self.backup_root / "temp"
        )

        # Real media directory used by the website.
        self.media_root = Path(
            "/home/nkavoshc/public_html/media"
        ).resolve()

        self.database_file = Path(
            settings.DATABASES["default"]["NAME"]
        ).resolve()

        self.backup_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.temp_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_backup(self):
        engine = settings.DATABASES[
            "default"
        ]["ENGINE"]

        if engine != "django.db.backends.sqlite3":
            raise RuntimeError(
                "این سرویس فقط از SQLite پشتیبانی می‌کند."
            )

        # Prevent silently creating database-only backups.
        media_files = self._get_media_files()

        timestamp = timezone.localtime().strftime(
            "%Y_%m_%d_%H_%M_%S"
        )

        unique_id = uuid.uuid4().hex[:12]

        backup_name = (
            f"backup_{timestamp}_{unique_id}"
        )

        work_dir = Path(
            tempfile.mkdtemp(
                prefix="backup_work_",
                dir=self.temp_root,
            )
        )

        database_dir = work_dir / "Database"
        media_dir = work_dir / "Media"
        info_dir = work_dir / "Information"

        for directory in (
            database_dir,
            media_dir,
            info_dir,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        final_zip = (
            self.backup_root
            / f"{backup_name}.zip"
        )

        temporary_zip = (
            self.backup_root
            / f".{backup_name}.partial"
        )

        published = False
        registered = False

        try:
            logger.info(
                "Starting backup: %s",
                backup_name,
            )

            self._backup_database(
                database_dir
            )

            self._backup_media(
                media_dir,
                media_files=media_files,
            )

            self._create_info_file(
                info_dir,
                database_dir,
                media_files=media_files,
            )

            self._create_zip(
                temporary_zip,
                work_dir,
            )

            self._verify_zip(
                temporary_zip
            )

            checksum = self._calculate_checksum(
                temporary_zip
            )

            file_size = (
                temporary_zip.stat().st_size
            )

            os.replace(
                temporary_zip,
                final_zip,
            )

            published = True

            Backup.objects.create(
                file_name=final_zip.name,
                file_size=file_size,
                checksum=checksum,
            )

            registered = True

            try:
                self._cleanup_old_backups()
            except Exception:
                logger.exception(
                    "Old backup cleanup failed."
                )

            logger.info(
                "Backup completed: %s",
                final_zip.name,
            )

            return final_zip

        except Exception:
            logger.exception(
                "Backup creation failed."
            )

            if published and not registered:
                final_zip.unlink(
                    missing_ok=True
                )

            raise

        finally:
            temporary_zip.unlink(
                missing_ok=True
            )

            shutil.rmtree(
                work_dir,
                ignore_errors=True,
            )

    def _get_media_files(self):
        """
        Collect all regular media files.

        Fail if media is missing or empty, instead
        of silently producing an incomplete backup.
        """
        if not self.media_root.is_dir():
            raise FileNotFoundError(
                "پوشه اصلی Media پیدا نشد: "
                f"{self.media_root}"
            )

        if (
            self.media_root == self.backup_root
            or self.backup_root.is_relative_to(
                self.media_root
            )
        ):
            raise ValueError(
                "پوشه Backup نباید داخل Media باشد."
            )

        files = []

        for source in self.media_root.rglob("*"):
            relative_path = source.relative_to(
                self.media_root
            )

            if source.is_symlink():
                raise ValueError(
                    "لینک نمادین در Media مجاز نیست: "
                    f"{relative_path}"
                )

            if source.is_file():
                files.append(source)

        if not files:
            raise ValueError(
                "پوشه Media خالی است. "
                "برای جلوگیری از ایجاد بکاپ ناقص، "
                "عملیات متوقف شد. "
                f"مسیر بررسی‌شده: {self.media_root}"
            )

        return sorted(files)

    def _backup_database(self, database_dir):
        if not self.database_file.is_file():
            raise FileNotFoundError(
                "فایل دیتابیس SQLite پیدا نشد."
            )

        target_file = (
            database_dir
            / self.database_file.name
        )

        source_connection = None
        target_connection = None

        try:
            connection.close()

            database_uri = (
                self.database_file.as_uri()
                + "?mode=ro"
            )

            source_connection = sqlite3.connect(
                database_uri,
                uri=True,
                timeout=30,
            )

            source_connection.execute(
                "PRAGMA busy_timeout = 30000"
            )

            target_connection = sqlite3.connect(
                str(target_file),
                timeout=30,
            )

            source_connection.backup(
                target_connection,
                pages=100,
                sleep=0.1,
            )

            target_connection.commit()

        finally:
            if target_connection is not None:
                target_connection.close()

            if source_connection is not None:
                source_connection.close()

        self._verify_database(
            target_file
        )

    @staticmethod
    def _verify_database(database_file):
        database_uri = (
            Path(database_file)
            .resolve()
            .as_uri()
            + "?mode=ro"
        )

        db = None

        try:
            db = sqlite3.connect(
                database_uri,
                uri=True,
                timeout=15,
            )

            result = db.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if not result or result[0] != "ok":
                raise ValueError(
                    "بررسی سلامت دیتابیس ناموفق بود."
                )

            tables = {
                row[0]
                for row in db.execute(
                    "SELECT name "
                    "FROM sqlite_master "
                    "WHERE type='table'"
                )
            }

            if "django_migrations" not in tables:
                raise ValueError(
                    "جدول django_migrations "
                    "در دیتابیس وجود ندارد."
                )

        finally:
            if db is not None:
                db.close()

    def _backup_media(
        self,
        media_dir,
        media_files=None,
    ):
        if media_files is None:
            media_files = self._get_media_files()

        for source in media_files:
            relative_path = source.relative_to(
                self.media_root
            )

            if source.is_symlink():
                raise ValueError(
                    f"لینک نمادین مجاز نیست: {relative_path}"
                )

            destination = (
                media_dir / relative_path
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                destination,
            )

        logger.info(
            "Media backup completed: %s files",
            len(media_files),
        )

    def _create_info_file(
        self,
        info_dir,
        database_dir,
        media_files=None,
    ):
        database_copy = (
            database_dir
            / self.database_file.name
        )

        if media_files is None:
            media_files = self._get_media_files()

        media_count = len(media_files)

        media_size = sum(
            file.stat().st_size
            for file in media_files
        )

        info = f"""
==============================
Backup Information
==============================

Project:
{settings.ROOT_URLCONF}

Created At:
{timezone.localtime():%Y-%m-%d %H:%M:%S}

Python:
{platform.python_version()}

Django:
{django.get_version()}

Database:
SQLite

Backup Method:
SQLite Online Backup API

Database File:
{database_copy.name}

Database Size:
{database_copy.stat().st_size} Bytes

Media Source:
{self.media_root}

Media Files:
{media_count}

Media Size:
{media_size} Bytes

Generated By:
BackupService

Restore Compatibility:
Database/
Media/
Information/
"""

        info_file = (
            info_dir / "backup_info.txt"
        )

        info_file.write_text(
            info.strip() + "\n",
            encoding="utf-8",
        )

    def _create_zip(
        self,
        zip_path,
        source_dir,
    ):
        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
            allowZip64=True,
        ) as zip_file:

            for file in sorted(
                source_dir.rglob("*")
            ):
                if file.is_symlink():
                    raise ValueError(
                        "لینک نمادین در بکاپ مجاز نیست."
                    )

                if not file.is_file():
                    continue

                zip_file.write(
                    filename=file,
                    arcname=file.relative_to(
                        source_dir
                    ).as_posix(),
                )

    @staticmethod
    def _verify_zip(zip_path):
        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as zip_file:

            bad_file = zip_file.testzip()

            if bad_file is not None:
                raise ValueError(
                    f"فایل ZIP خراب است: {bad_file}"
                )

            names = zip_file.namelist()

            database_files = [
                name
                for name in names
                if (
                    name.startswith("Database/")
                    and name.endswith(".sqlite3")
                    and len(Path(name).parts) == 2
                )
            ]

            media_files = [
                name
                for name in names
                if (
                    name.startswith("Media/")
                    and not name.endswith("/")
                )
            ]

            if len(database_files) != 1:
                raise ValueError(
                    "بکاپ باید دقیقاً یک دیتابیس "
                    "SQLite داشته باشد."
                )

            if not media_files:
                raise ValueError(
                    "هیچ فایل Media داخل بکاپ وجود ندارد."
                )

            if "Information/backup_info.txt" not in names:
                raise ValueError(
                    "فایل اطلاعات بکاپ وجود ندارد."
                )

    @staticmethod
    def _calculate_checksum(file_path):
        sha256 = hashlib.sha256()

        with Path(file_path).open("rb") as file:
            for chunk in iter(
                lambda: file.read(
                    1024 * 1024
                ),
                b"",
            ):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _cleanup_old_backups(self):
        """
        Keep the latest 30 registered backups.

        Unregistered ZIP files are not touched.
        """
        backup_ids = list(
            Backup.objects.order_by(
                "-created_at",
                "-pk",
            ).values_list(
                "pk",
                flat=True,
            )
        )

        old_backup_ids = backup_ids[
            self.KEEP_LAST_BACKUPS:
        ]

        for backup_id in old_backup_ids:
            try:
                backup = Backup.objects.get(
                    pk=backup_id
                )

                backup_path = (
                    self.backup_root
                    / backup.file_name
                )

                if (
                    backup_path.parent.resolve()
                    != self.backup_root
                    or backup_path.is_symlink()
                    or backup_path.suffix.lower() != ".zip"
                ):
                    raise ValueError(
                        "مسیر فایل بکاپ نامعتبر است."
                    )

                if backup_path.exists():
                    backup_path.unlink()

                backup.delete()

            except Backup.DoesNotExist:
                continue

            except Exception:
                logger.exception(
                    "Failed to delete old backup: %s",
                    backup_id,
                )
