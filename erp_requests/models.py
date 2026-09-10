from django.db import models


class Request(models.Model):

    STATUS_CHOICES = [
        ("NEW", "جدید"),
        ("SENT_TO_EXECUTION", "ارسال شده به اجرایات"),
        ("IN_EXECUTION", "در حال بررسی اجرایات"),
        ("SENT_TO_WAREHOUSE", "ارسال شده به انبار"),
        ("IN_WAREHOUSE", "در حال بررسی انبار"),
        ("WAITING_REQUESTER", "در انتظار درخواست‌کننده"),
        ("COMPLETED_BY_REQUESTER", "اتمام کار توسط درخواست‌کننده"),
        ("SENT_TO_FINANCE", "ارسال شده به مالی"),
        ("INVOICED", "فاکتور صادر شده"),
        ("COMPLETED", "تکمیل نهایی"),
        ("REJECTED", "رد شده"),
        ("CANCELLED", "لغو شده"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "کم"),
        ("NORMAL", "عادی"),
        ("HIGH", "زیاد"),
        ("URGENT", "فوری"),
    ]

    # =====================================================
    # اطلاعات اصلی درخواست
    # =====================================================

    number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد درخواست",
        editable=False,
    )

    project_name = models.CharField(
        max_length=200,
        verbose_name="نام پروژه",
    )

    description = models.TextField(
        blank=True,
        verbose_name="شرح درخواست",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="NORMAL",
        verbose_name="اولویت",
    )

    # =====================================================
    # اقلام درخواستی
    # =====================================================

    item_1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مورد ۱",
    )

    quantity_1 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد ۱",
    )

    item_2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مورد ۲",
    )

    quantity_2 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد ۲",
    )

    item_3 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مورد ۳",
    )

    quantity_3 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد ۳",
    )

    item_4 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مورد ۴",
    )

    quantity_4 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد ۴",
    )

    item_5 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مورد ۵",
    )

    quantity_5 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="تعداد ۵",
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

    requester_note = models.TextField(
        blank=True,
        verbose_name="توضیحات درخواست",
    )

    # =====================================================
    # تاریخ‌ها
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت ثبت",
    )

    sent_to_execution_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت ارسال به اجرایات",
    )

    requester_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت اتمام توسط درخواست‌کننده",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ و ساعت تکمیل نهایی",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:
        verbose_name = "درخواست"
        verbose_name_plural = "درخواست‌ها"
        ordering = ["-created_at"]

    # =====================================================
    # نمایش
    # =====================================================

    def __str__(self):
        return f"{self.number} - {self.project_name}"

    # =====================================================
    # تولید خودکار کد درخواست
    # =====================================================

    def save(self, *args, **kwargs):

        if not self.number:

            last_request = (
                Request.objects
                .order_by("-id")
                .first()
            )

            if last_request and last_request.number:

                try:
                    last_number = int(
                        last_request.number.replace("R-", "")
                    )
                except ValueError:
                    last_number = 0

            else:
                last_number = 0

            self.number = f"R-{last_number + 1:05d}"

        super().save(*args, **kwargs)