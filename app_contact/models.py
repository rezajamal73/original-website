from django.db import models
import jdatetime


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ("new", "جدید"),
        ("seen", "دیده شده"),
    )

    first_name = models.CharField("نام", max_length=100)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    phone = models.CharField("شماره تماس", max_length=20)
    email = models.EmailField("ایمیل", blank=True)
    subject = models.CharField("موضوع", max_length=255)
    message = models.TextField("پیام")

    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(
        "تاریخ ارسال (میلادی)",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} | {self.subject}"

    # ---------- تاریخ ایجاد (شمسی) ----------
    @property
    def created_at_fa(self):
        if not self.created_at:
            return "—"

        j_date = jdatetime.datetime.fromgregorian(
            datetime=self.created_at
        )
        return j_date.strftime("%Y/%m/%d %H:%M")

    created_at_fa.fget.short_description = "تاریخ ایجاد"

    # ---------- نام و نام خانوادگی ----------
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    full_name.fget.short_description = "نام و نام خانوادگی"