import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings

from .models import Backup


class RestoreService:
    """
    بازیابی نسخه پشتیبان
    """

    def __init__(self, backup: Backup):

        self.backup = backup

        self.backup_file = backup.backup_path

        self.database_target = Path(
            settings.DATABASES["default"]["NAME"]
        )

        self.media_root = Path(
            settings.MEDIA_ROOT
        )

        self.temp_dir = Path(
            tempfile.mkdtemp(
                prefix="restore_",
            )
        )

    ########################################################
    # Restore
    ########################################################

    def restore(self):

        if not self.backup.file_exists:

            raise FileNotFoundError(
                "فایل نسخه پشتیبان وجود ندارد."
            )

        self._verify_checksum()

        try:

            ################################################
            # Extract ZIP
            ################################################

            with zipfile.ZipFile(
                self.backup_file,
                "r",
            ) as zip_file:

                if zip_file.testzip():

                    raise ValueError(
                        "فایل ZIP خراب است."
                    )

                self._safe_extract(
                    zip_file,
                    self.temp_dir,
                )

            ################################################
            # Database
            ################################################

            database_dir = (
                self.temp_dir / "Database"
            )

            if not database_dir.is_dir():

                raise FileNotFoundError(
                    "پوشه Database پیدا نشد."
                )

            database_file = next(
                database_dir.glob("*.sqlite3"),
                None,
            )

            if database_file is None:

                raise FileNotFoundError(
                    "فایل دیتابیس پیدا نشد."
                )

            shutil.copy2(
                database_file,
                self.database_target,
            )

            ################################################
            # Media
            ################################################

            media_backup = (
                self.temp_dir / "Media"
            )

            if media_backup.is_dir():

                if self.media_root.exists():

                    shutil.rmtree(
                        self.media_root,
                        ignore_errors=True,
                    )

                shutil.copytree(
                    media_backup,
                    self.media_root,
                )

        finally:

            shutil.rmtree(
                self.temp_dir,
                ignore_errors=True,
            )

    ########################################################
    # Verify SHA-256
    ########################################################

    def _verify_checksum(self):

        sha256 = hashlib.sha256()

        with self.backup_file.open("rb") as file:

            while chunk := file.read(8192):
                sha256.update(chunk)

        if (
            sha256.hexdigest()
            != self.backup.checksum
        ):

            raise ValueError(
                "مقدار SHA-256 فایل با مقدار ذخیره‌شده مطابقت ندارد."
            )

    ########################################################
    # Safe Extract
    ########################################################

    @staticmethod
    def _safe_extract(
        zip_file,
        destination,
    ):

        destination = destination.resolve()

        for member in zip_file.infolist():

            target = (
                destination / member.filename
            ).resolve()

            if not str(target).startswith(
                str(destination)
            ):

                raise ValueError(
                    "ZIP شامل مسیر غیرمجاز است."
                )

        zip_file.extractall(
            destination,
        )