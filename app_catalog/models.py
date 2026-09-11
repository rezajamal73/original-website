from django.db import models
from django.core.validators import FileExtensionValidator
import jdatetime


class CompanyCatalog(models.Model):
    """
    Single company catalog (PDF)
    """

    title_fa = models.CharField(
        max_length=200,
        verbose_name="عنوان فارسی"
    )
    title_en = models.CharField(
        max_length=200,
        verbose_name="عنوان انگلیسی"
    )

    description_fa = models.TextField(
        blank=True,
        verbose_name="توضیحات فارسی"
    )
    description_en = models.TextField(
        blank=True,
        verbose_name="توضیحات انگلیسی"
    )

    pdf_file = models.FileField(
        upload_to="catalog/",
        validators=[FileExtensionValidator(["pdf"])],
        verbose_name="فایل PDF"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "کاتالوگ شرکت"
        verbose_name_plural = "کاتالوگ شرکت"

    def __str__(self) -> str:
        return self.title_fa

    # =========================
    # Date Helpers (Professional)
    # =========================
    @property
    def updated_at_gregorian(self) -> str:
        """
        Return formatted Gregorian date
        """
        return self.updated_at.strftime("%Y-%m-%d")

    @property
    def updated_at_jalali(self) -> str:
        """
        Return formatted Jalali (Shamsi) date
        """
        jalali_date = jdatetime.datetime.fromgregorian(
            datetime=self.updated_at
        )
        return jalali_date.strftime("%Y/%m/%d")
