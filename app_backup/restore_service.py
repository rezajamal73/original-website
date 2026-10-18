
import hashlib
import hmac
import logging
import shutil
import sqlite3
import stat
import tempfile
import zipfile

from pathlib import Path, PurePosixPath

from django.conf import settings

from .models import Backup


logger = logging.getLogger(__name__)


class RestoreService:
    """
    Safe backup validation and staging service.

    IMPORTANT:
    This service DOES NOT restore the live database
    or replace the live media directory.

    It validates the backup and prepares a temporary
    copy for verification only.
    """

    MAX_FILES = 50000
    MAX_UNCOMPRESSED_SIZE = 10 * 1024**3
    MAX_SINGLE_FILE_SIZE = 5 * 1024**3
    MAX_COMPRESSION_RATIO = 1000

    def __init__(self, backup: Backup):

        self.backup = backup

        self.backup_file = Path(
            backup.backup_path
        )

        self.database_target = Path(
            settings.DATABASES["default"]["NAME"]
        )

        self.media_root = Path(
            settings.MEDIA_ROOT
        )

        self.temp_dir = None

    ########################################################
    # Main Restore Entry
    ########################################################

    def restore(self):
        """
        Validate and stage the backup.

        No live data is modified.
        """

        if (
            settings.DATABASES["default"]["ENGINE"]
            != "django.db.backends.sqlite3"
        ):
            raise RuntimeError(
                "این سرویس فقط برای SQLite طراحی شده است."
            )

        if not self.backup.file_exists:
            raise FileNotFoundError(
                "فایل نسخه پشتیبان وجود ندارد."
            )

        self._verify_checksum()

        self.temp_dir = Path(
            tempfile.mkdtemp(
                prefix="restore_validation_"
            )
        )

        try:

            with zipfile.ZipFile(
                self.backup_file,
                "r",
            ) as zip_file:

                members = self._validate_zip(
                    zip_file
                )

                database_members = [
                    member
                    for member in members
                    if (
                        member.filename.startswith(
                            "Database/"
                        )
                        and member.filename.endswith(
                            ".sqlite3"
                        )
                        and not member.is_dir()
                        and len(
                            PurePosixPath(
                                member.filename
                            ).parts
                        ) == 2
                    )
                ]

                if len(database_members) != 1:
                    raise ValueError(
                        "بکاپ باید دقیقاً یک فایل دیتابیس "
                        "SQLite در پوشه Database داشته باشد."
                    )

                database_member = database_members[0]

                staged_database = (
                    self.temp_dir
                    / "database.sqlite3"
                )

                with zip_file.open(
                    database_member,
                    "r",
                ) as source:

                    with staged_database.open(
                        "wb"
                    ) as destination:

                        shutil.copyfileobj(
                            source,
                            destination,
                            length=1024 * 1024,
                        )

                self._verify_sqlite(
                    staged_database
                )

                media_members = [
                    member
                    for member in members
                    if (
                        member.filename.startswith(
                            "Media/"
                        )
                        and not member.is_dir()
                    )
                ]

                media_file_count = len(
                    media_members
                )

            logger.info(
                "Backup validated successfully: %s",
                self.backup.file_name,
            )

            return {
                "valid": True,
                "database_valid": True,
                "database_name": (
                    database_member.filename
                ),
                "media_files": media_file_count,
                "restored": False,
                "message": (
                    "نسخه پشتیبان بررسی و تأیید شد. "
                    "هیچ اطلاعاتی روی سایت اصلی "
                    "جایگزین نشده است."
                ),
            }

        finally:

            if self.temp_dir is not None:

                shutil.rmtree(
                    self.temp_dir,
                    ignore_errors=True,
                )

                self.temp_dir = None

    ########################################################
    # Verify SHA-256
    ########################################################

    def _verify_checksum(self):

        sha256 = hashlib.sha256()

        with self.backup_file.open(
            "rb"
        ) as file:

            for chunk in iter(
                lambda: file.read(
                    1024 * 1024
                ),
                b"",
            ):
                sha256.update(chunk)

        actual_checksum = sha256.hexdigest()

        expected_checksum = (
            self.backup.checksum or ""
        ).strip().lower()

        if not hmac.compare_digest(
            actual_checksum,
            expected_checksum,
        ):
            raise ValueError(
                "مقدار SHA-256 فایل بکاپ "
                "با مقدار ثبت‌شده مطابقت ندارد."
            )

    ########################################################
    # Validate ZIP
    ########################################################

    def _validate_zip(
        self,
        zip_file,
    ):

        members = zip_file.infolist()

        if len(members) > self.MAX_FILES:
            raise ValueError(
                "تعداد فایل‌های ZIP بیش از حد مجاز است."
            )

        total_size = 0
        seen_paths = set()

        for member in members:

            name = member.filename

            if not name:
                raise ValueError(
                    "نام یکی از فایل‌های ZIP خالی است."
                )

            if "\\" in name:
                raise ValueError(
                    "مسیر غیرمجاز در فایل ZIP."
                )

            path = PurePosixPath(name)

            if (
                path.is_absolute()
                or ".." in path.parts
                or "." in path.parts
                or ":" in name
            ):
                raise ValueError(
                    f"مسیر غیرمجاز: {name}"
                )

            if name in seen_paths:
                raise ValueError(
                    f"فایل تکراری در ZIP: {name}"
                )

            seen_paths.add(name)

            mode = (
                member.external_attr >> 16
            )

            file_type = stat.S_IFMT(mode)

            if file_type not in (
                0,
                stat.S_IFREG,
                stat.S_IFDIR,
            ):
                raise ValueError(
                    "ZIP شامل لینک یا فایل غیرعادی است."
                )

            if member.flag_bits & 0x1:
                raise ValueError(
                    "فایل ZIP رمزگذاری‌شده پشتیبانی نمی‌شود."
                )

            if (
                member.file_size
                > self.MAX_SINGLE_FILE_SIZE
            ):
                raise ValueError(
                    "حجم یکی از فایل‌های بکاپ "
                    "بیش از حد مجاز است."
                )

            total_size += member.file_size

            if (
                total_size
                > self.MAX_UNCOMPRESSED_SIZE
            ):
                raise ValueError(
                    "حجم استخراج‌شده بکاپ "
                    "بیش از حد مجاز است."
                )

            if (
                member.file_size > 0
                and member.compress_size == 0
            ):
                raise ValueError(
                    "نسبت فشرده‌سازی غیرمجاز است."
                )

            if member.compress_size > 0:

                ratio = (
                    member.file_size
                    / member.compress_size
                )

                if (
                    ratio
                    > self.MAX_COMPRESSION_RATIO
                ):
                    raise ValueError(
                        "نسبت فشرده‌سازی مشکوک است."
                    )

        bad_member = zip_file.testzip()

        if bad_member is not None:
            raise ValueError(
                f"فایل ZIP خراب است: {bad_member}"
            )

        return members

    ########################################################
    # Verify SQLite Database
    ########################################################

    @staticmethod
    def _verify_sqlite(
        database_file,
    ):

        if not database_file.is_file():
            raise FileNotFoundError(
                "فایل دیتابیس پیدا نشد."
            )

        connection = None

        try:

            database_uri = (
                database_file.resolve().as_uri()
                + "?mode=ro"
            )

            connection = sqlite3.connect(
                database_uri,
                uri=True,
                timeout=10,
            )

            result = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if (
                result is None
                or result[0] != "ok"
            ):
                raise ValueError(
                    "ساختار دیتابیس SQLite سالم نیست."
                )

            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name "
                    "FROM sqlite_master "
                    "WHERE type = 'table'"
                ).fetchall()
            }

            if "django_migrations" not in tables:
                raise ValueError(
                    "دیتابیس بکاپ فاقد جدول "
                    "django_migrations است."
                )

        except sqlite3.DatabaseError as error:

            raise ValueError(
                "فایل SQLite معتبر نیست."
            ) from error

        finally:

            if connection is not None:
                connection.close()

    ########################################################
    # Safe Extract Helper
    ########################################################

    @staticmethod
    def _safe_extract(
        zip_file,
        destination,
    ):
        """
        Compatibility helper.

        Validates every path and rejects links
        before extracting archive contents.
        """

        destination = Path(
            destination
        ).resolve()

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        members = zip_file.infolist()

        total_size = 0

        for member in members:

            name = member.filename

            if (
                not name
                or "\\" in name
                or ":" in name
            ):
                raise ValueError(
                    "مسیر غیرمجاز در ZIP."
                )

            relative_path = PurePosixPath(
                name
            )

            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or "." in relative_path.parts
            ):
                raise ValueError(
                    "مسیر غیرمجاز در ZIP."
                )

            mode = member.external_attr >> 16

            if stat.S_IFMT(mode) not in (
                0,
                stat.S_IFREG,
                stat.S_IFDIR,
            ):
                raise ValueError(
                    "لینک یا فایل غیرمجاز در ZIP."
                )

            target = (
                destination / name
            ).resolve()

            if not target.is_relative_to(
                destination
            ):
                raise ValueError(
                    "مسیر خارج از پوشه مقصد است."
                )

            total_size += member.file_size

            if (
                member.file_size
                > RestoreService.MAX_SINGLE_FILE_SIZE
                or total_size
                > RestoreService.MAX_UNCOMPRESSED_SIZE
            ):
                raise ValueError(
                    "حجم فایل‌های استخراجی بیش از حد مجاز است."
                )

        for member in members:

            target = (
                destination / member.filename
            ).resolve()

            if member.is_dir():

                target.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                continue

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with zip_file.open(
                member,
                "r",
            ) as source:

                with target.open(
                    "wb"
                ) as output:

                    shutil.copyfileobj(
                        source,
                        output,
                        length=1024 * 1024,
                    )
