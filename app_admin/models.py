
from django.conf import settings
from django.db import models
from django.utils import timezone


class SecurityIPRule(models.Model):
    RULE_CHOICES = [
        ("allow", "IP مجاز"),
        ("block", "IP مسدود"),
    ]

    ip_address = models.GenericIPAddressField(
        verbose_name="آدرس IP",
    )

    rule_type = models.CharField(
        max_length=10,
        choices=RULE_CHOICES,
        verbose_name="نوع قانون",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توضیحات",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پایان اعتبار",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ثبت‌کننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    class Meta:
        verbose_name = "قانون IP"
        verbose_name_plural = "مدیریت IPهای غیرمجاز"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_rule_type_display()} - {self.ip_address}"

    @property
    def is_effective(self):
        return (
            self.is_active
            and (
                self.expires_at is None
                or self.expires_at > timezone.now()
            )
        )


class AllowedIP(SecurityIPRule):
    """
    Separate admin view for allowed IP addresses.
    Uses the existing SecurityIPRule database table.
    """

    class Meta:
        proxy = True
        verbose_name = "IP مجاز"
        verbose_name_plural = "مدیریت IPهای مجاز"
        ordering = ["-created_at"]


class SecurityAuditLog(models.Model):
    action = models.CharField(
        max_length=100,
        verbose_name="عملیات",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP مرتبط",
    )

    details = models.TextField(
        blank=True,
        verbose_name="جزئیات",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مدیر انجام‌دهنده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان عملیات",
    )

    class Meta:
        verbose_name = "گزارش عملیات امنیتی"
        verbose_name_plural = "سوابق عملیات امنیتی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.created_at}"
