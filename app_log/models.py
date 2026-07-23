from django.db import models
from django.contrib.auth import get_user_model
import jdatetime
from django.utils import timezone

User = get_user_model()


class SystemLog(models.Model):
    ACTIONS = (
        ("create", "ثبت"),
        ("update", "ویرایش"),
        ("delete", "حذف"),
    )

    app_name = models.CharField(
        max_length=100,
        verbose_name="اپلیکیشن",
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name="مدل",
    )

    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه رکورد",
    )

    object_name = models.CharField(
        max_length=255,
        verbose_name="نام رکورد",
    )

    action = models.CharField(
        max_length=10,
        choices=ACTIONS,
        verbose_name="عملیات",
    )

    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="اطلاعات قبلی",
    )

    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="اطلاعات جدید",
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="کاربر",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ثبت",
    )

    def created_at_jalali(self):
        local_time = timezone.localtime(self.created_at)
        return jdatetime.datetime.fromgregorian(
            datetime=local_time
        ).strftime("%Y/%m/%d %H:%M:%S")

    created_at_jalali.short_description = "تاریخ شمسی"

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "📜 لاگ سیستم"
        verbose_name_plural = "📜 لاگ‌های سیستم"

    def __str__(self):
        return f"{self.get_action_display()} | {self.app_name}.{self.model_name} | {self.object_name}"