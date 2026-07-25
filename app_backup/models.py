from pathlib import Path

from django.conf import settings
from django.db import models


BACKUP_DIRECTORY = Path(settings.BASE_DIR) / "backup"
BACKUP_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


class Backup(models.Model):
    file_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="نام فایل",
        help_text="نام فایل ZIP نسخه پشتیبان",
    )

    file_size = models.PositiveBigIntegerField(
        verbose_name="حجم فایل (Byte)",
        help_text="حجم واقعی فایل بر حسب بایت",
    )

    checksum = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="SHA-256",
        help_text="هش فایل برای بررسی سلامت فایل",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "نسخه پشتیبان"
        verbose_name_plural = "نسخه‌های پشتیبان"
        ordering = ("-created_at",)

    def __str__(self):
        return self.file_name

    def __repr__(self):
        return f"<Backup: {self.file_name}>"

    @property
    def backup_path(self) -> Path:
        """
        مسیر کامل فایل ZIP
        """
        return BACKUP_DIRECTORY / self.file_name

    @property
    def file_exists(self) -> bool:
        """
        بررسی وجود فایل روی دیسک
        """
        return self.backup_path.is_file()

    @property
    def size(self) -> str:
        """
        نمایش حجم فایل به صورت خوانا
        """
        size = float(self.file_size)

        for unit in ("Byte", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return (
                    f"{int(size)} {unit}"
                    if unit == "Byte"
                    else f"{size:.2f} {unit}"
                )
            size /= 1024

    def delete(self, *args, **kwargs):
        """
        حذف فایل ZIP از روی دیسک هنگام حذف رکورد
        """
        try:
            self.backup_path.unlink(
                missing_ok=True,
            )
        except OSError:
            pass

        return super().delete(
            *args,
            **kwargs,
        )