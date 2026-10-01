from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jdatetime


class Visit(models.Model):
    """مدل ثبت بازدیدهای سایت"""

    DEVICE_CHOICES = (
        ("desktop", "دسکتاپ"),
        ("mobile", "موبایل"),
        ("tablet", "تبلت"),
        ("bot", "ربات"),
        ("unknown", "نامشخص"),
    )

    OS_CHOICES = (
        ("windows", "ویندوز"),
        ("mac", "مک"),
        ("linux", "لینوکس"),
        ("android", "اندروید"),
        ("ios", "iOS"),
        ("other", "سایر"),
        ("unknown", "نامشخص"),
    )

    BROWSER_CHOICES = (
        ("chrome", "کروم"),
        ("firefox", "فایرفاکس"),
        ("safari", "سافاری"),
        ("edge", "اج"),
        ("opera", "اپرا"),
        ("ie", "اینترنت اکسپلورر"),
        ("other", "سایر"),
        ("unknown", "نامشخص"),
    )

    # ============ فیلدهای اصلی (قبلی) ============
    ip = models.GenericIPAddressField(
        db_index=True,
        verbose_name="IP",
        help_text="آدرس IP بازدیدکننده",
    )

    path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        verbose_name="مسیر صفحه",
    )

    method = models.CharField(
        max_length=10,
        default="GET",
        blank=True,
        verbose_name="متد",
    )

    user_agent = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="مرورگر",
    )

    referer = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="ارجاع‌دهنده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="اولین بازدید",
    )

    last_seen = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name="آخرین فعالیت",
    )

    visit_count = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد بازدید",
    )

    is_bot = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="ربات",
    )

    # ============ فیلدهای جدید (دستگاه) ============
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES,
        default="unknown",
        db_index=True,
        verbose_name="نوع دستگاه",
    )

    os = models.CharField(
        max_length=20,
        choices=OS_CHOICES,
        default="unknown",
        db_index=True,
        verbose_name="سیستم‌عامل",
    )

    browser = models.CharField(
        max_length=20,
        choices=BROWSER_CHOICES,
        default="unknown",
        db_index=True,
        verbose_name="مرورگر",
    )

    device_model = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="مدل دستگاه",
        help_text="مثلاً iPhone 14, Samsung Galaxy S23",
    )

    screen_resolution = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="رزولوشن صفحه",
    )

    language = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="زبان",
    )

    class Meta:
        ordering = ("-last_seen",)
        verbose_name = "بازدید"
        verbose_name_plural = "بازدیدها"
        indexes = [
            models.Index(fields=["ip", "created_at"]),
            models.Index(fields=["path", "created_at"]),
            models.Index(fields=["is_bot", "created_at"]),
            models.Index(fields=["device_type", "created_at"]),
            models.Index(fields=["os", "created_at"]),
            models.Index(fields=["browser", "created_at"]),
        ]

    def __str__(self):
        return f"{self.ip} | {self.page_name}"

    @property
    def page_name(self):
        pages = {
            "/": "صفحه اصلی",
            "/about/": "درباره ما",
            "/contact/": "تماس با ما",
            "/blog/": "وبلاگ",
            "/news/": "اخبار",
            "/product/": "محصولات",
            "/catalog/": "کاتالوگ",
            "/sale/": "فروش",
            "/chart/": "چارت سازمانی",
            "/tender/": "مناقصات",
            "/tender-holding/": "مناقصات هلدینگ",
            "/auction/": "مزایدات",
            "/inquiry/": "استعلام‌ها",
            "/reports/": "گزارش‌ها",
            "/hr/": "فرصت‌های شغلی",
            "/resume/": "رزومه‌ها",
            "/media/": "رسانه",
        }
        return pages.get(self.path, self.path)

    @property
    def created_at_j(self):
        if not self.created_at:
            return "-"
        return jdatetime.datetime.fromgregorian(
            datetime=self.created_at
        ).strftime("%Y/%m/%d %H:%M")

    @property
    def last_seen_j(self):
        if not self.last_seen:
            return "-"
        return jdatetime.datetime.fromgregorian(
            datetime=self.last_seen
        ).strftime("%Y/%m/%d %H:%M")

    @property
    def device_display(self):
        parts = []
        if self.device_type and self.device_type != "unknown":
            parts.append(self.get_device_type_display())
        if self.device_model:
            parts.append(self.device_model)
        if self.os and self.os != "unknown":
            parts.append(self.get_os_display())
        if self.browser and self.browser != "unknown":
            parts.append(self.get_browser_display())
        return " - ".join(parts) if parts else "نامشخص"

    @classmethod
    def get_stats(cls, days=30):
        start_date = timezone.now() - timezone.timedelta(days=days)
        qs = cls.objects.filter(created_at__gte=start_date)
        total = cls.objects.count()
        today = cls.objects.filter(
            created_at__date=timezone.localdate()
        ).count()
        bot_count = qs.filter(is_bot=True).count()
        unique_visitors = qs.values("ip").distinct().count()
        top_paths = (
            qs.values("path")
            .annotate(visits=Sum("visit_count"))
            .order_by("-visits")[:10]
        )
        top_ips = (
            qs.values("ip")
            .annotate(visits=Sum("visit_count"))
            .order_by("-visits")[:10]
        )
        return {
            "total": total,
            "today": today,
            "unique_visitors": unique_visitors,
            "bot_count": bot_count,
            "top_paths": top_paths,
            "top_ips": top_ips,
            "period_days": days,
        }