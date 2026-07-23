from django.db import models
from django.core.validators import FileExtensionValidator




class ResumeProvince(models.Model):
    province_name_fa = models.CharField(
        max_length=100,
        verbose_name="نام استان یا شهر (فارسی)",
        help_text="مثال: تهران، اصفهان، شیراز"
    )

    province_name_en = models.CharField(
        max_length=100,
        verbose_name="نام استان یا شهر (انگلیسی)",
        help_text="Example: Tehran, Isfahan, Shiraz"
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش"
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = " شهر یا استان"
        verbose_name_plural = " شهرها و استان‌ها"

    def __str__(self):
        return self.province_name_fa


class Resume(models.Model):
    project_name_fa = models.CharField(
        max_length=200,
        verbose_name="نام پروژه (فارسی)",
    )

    project_name_en = models.CharField(
        max_length=200,
        verbose_name="نام پروژه (انگلیسی)",
    )

    province = models.ForeignKey(
        ResumeProvince,
        on_delete=models.PROTECT,
        related_name="resumes",
        verbose_name="استان / شهر",
    )

    svg_file = models.FileField(
        upload_to="resume/svg/",
        validators=[FileExtensionValidator(["svg"])],
        verbose_name="فایل SVG",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    class Meta:
        ordering = ("display_order",)
        verbose_name = "رزومه"
        verbose_name_plural = "رزومه‌ها"

    def __str__(self):
        return f"{self.project_name_fa} - {self.province.province_name_fa}"
