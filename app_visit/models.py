from django.db import models
from django.utils.translation import gettext_lazy as _


class Visit(models.Model):
    """مدل ثبت بازدیدهای سایت"""

    # فیلدهای اصلی
    ip = models.GenericIPAddressField(
        db_index=True,
        verbose_name=_("IP"),
        help_text=_("آدرس IP بازدیدکننده"),
    )

    path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("Page"),
        help_text=_("مسیر درخواستی"),
    )

    method = models.CharField(
        max_length=10,
        blank=True,
        default="GET",
        verbose_name=_("HTTP Method"),
        help_text=_("متود درخواست HTTP"),
    )

    user_agent = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("User Agent"),
        help_text=_("مرورگر و دستگاه کاربر"),
    )

    referer = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("Referer"),
        help_text=_("صفحه مبدا"),
    )

    # فیلدهای زمانی
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("First Visit"),
    )

    last_seen = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name=_("Last Activity"),
    )

    # فیلدهای آماری
    visit_count = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Visit Count"),
        help_text=_("تعداد بازدیدهای این IP از همان مسیر"),
    )

    is_bot = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Bot"),
        help_text=_("آیا این بازدید توسط ربات است؟"),
    )

    class Meta:
        ordering = ("-last_seen",)
        verbose_name = "بازدید"
        verbose_name_plural = "بازدیدها"
        indexes = [
            models.Index(fields=["ip", "created_at"]),
            models.Index(fields=["path", "created_at"]),
            models.Index(fields=["is_bot", "created_at"]),
        ]

    def __str__(self):
        return f"{self.ip} - {self.path} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def get_stats(cls, days=30):
        """دریافت آمار بازدیدها"""
        from django.db.models import Count, Q
        from django.utils import timezone

        now = timezone.now()
        start_date = now - timezone.timedelta(days=days)

        # آمار کلی
        total = cls.objects.count()
        today = cls.objects.filter(created_at__date=now.date()).count()

        # آمار مسیرها
        top_paths = cls.objects.filter(
            created_at__gte=start_date
        ).values('path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # آمار IP‌ها
        top_ips = cls.objects.filter(
            created_at__gte=start_date
        ).values('ip').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # آمار ربات‌ها
        bot_count = cls.objects.filter(
            is_bot=True,
            created_at__gte=start_date
        ).count()

        # بازدیدهای منحصر به فرد
        unique_visitors = cls.objects.filter(
            created_at__gte=start_date
        ).values('ip').distinct().count()

        return {
            'total': total,
            'today': today,
            'unique_visitors': unique_visitors,
            'bot_count': bot_count,
            'top_paths': top_paths,
            'top_ips': top_ips,
            'period_days': days,
        }