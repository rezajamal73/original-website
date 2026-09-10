
from django.db import models

from erp_requests.models import Request


# =========================================================
# درخواست اجرایات
# =========================================================

class ExecutionRequest(models.Model):

    STATUS_CHOICES = [
        ("NEW", "جدید"),
        ("SEEN", "دیده شد"),
        ("IN_PROGRESS", "در حال اجرا"),
        ("WAITING_WAREHOUSE", "در انتظار انبار"),
        ("COMPLETED", "اجرایات تکمیل شد"),
        ("REJECTED", "رد شد"),
    ]

    # =====================================================
    # اتصال به درخواست اصلی
    # =====================================================

    request = models.OneToOneField(
        Request,
        on_delete=models.PROTECT,
        related_name="execution_request",
        verbose_name="درخواست اصلی",
    )

    # =====================================================
    # اطلاعات درخواست
    # =====================================================

    request_number = models.CharField(
        max_length=50,
        verbose_name="شماره درخواست",
    )

    project_name = models.CharField(
        max_length=200,
        verbose_name="نام پروژه",
    )

    # =====================================================
    # مسئول اجرایات
    # =====================================================

    executor = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="execution_requests",
        verbose_name="مجری",
    )

    # =====================================================
    # وضعیت
    # =====================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="NEW",
        verbose_name="وضعیت",
    )

    # =====================================================
    # توضیحات
    # =====================================================

    description = models.TextField(
        blank=True,
        verbose_name="شرح درخواست",
    )

    requester_description = models.TextField(
        blank=True,
        verbose_name="شرح درخواست",
    )

    execution_description = models.TextField(
        blank=True,
        verbose_name="گزارش اجرایات",
    )

    # =====================================================
    # زمان‌ها
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت ارسال",
    )

    seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت مشاهده",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="شروع اجرا",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="پایان اجرایات",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:
        verbose_name = "درخواست اجرایات"
        verbose_name_plural = "درخواست‌های اجرایات"
        ordering = ["-created_at"]

    # =====================================================
    # نمایش
    # =====================================================

    def __str__(self):
        return f"{self.request_number} - {self.project_name}"

    # =====================================================
    # ذخیره
    # =====================================================

    def save(self, *args, **kwargs):

        if self.request_id:

            self.request_number = self.request.number
            self.project_name = self.request.project_name
            self.description = self.request.description
            self.requester_description = self.request.requester_note

        super().save(*args, **kwargs)


# =========================================================
# اقلام اجرایات
# =========================================================

class ExecutionItem(models.Model):

    execution = models.ForeignKey(
        ExecutionRequest,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="درخواست اجرایات",
    )

    item_number = models.PositiveSmallIntegerField(
        verbose_name="شماره قلم",
    )

    item_name = models.CharField(
        max_length=200,
        verbose_name="نام قلم",
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="تعداد",
    )

    unit = models.CharField(
        max_length=30,
        default="عدد",
        verbose_name="واحد",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:
        verbose_name = "قلم اجرایات"
        verbose_name_plural = "اقلام اجرایات"
        ordering = ["item_number"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "execution",
                    "item_number",
                ],
                name="unique_execution_item_number",
            )
        ]

    # =====================================================
    # نمایش
    # =====================================================

    def __str__(self):
        return (
            f"{self.execution.request_number} - "
            f"{self.item_name}"
        )

