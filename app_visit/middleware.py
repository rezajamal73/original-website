import logging
from datetime import timedelta
from typing import Optional
import re

from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from .models import Visit

logger = logging.getLogger(__name__)


class VisitMiddleware:
    """
    Middleware برای ثبت بازدیدها با بهینه‌سازی و جلوگیری از ثبت تکراری
    """

    # لیست ربات‌های شناخته شده
    BOT_PATTERNS = [
        r'bot',
        r'crawler',
        r'spider',
        r'googlebot',
        r'bingbot',
        r'slurp',
        r'duckduckbot',
        r'baiduspider',
        r'yandexbot',
        r'facebookexternalhit',
        r'twitterbot',
        r'linkedinbot',
        r'pinterestbot',
        r'semrushbot',
        r'ahrefsbot',
        r'majestic',
        r'rogerbot',
        r'exabot',
        r'ia_archiver',
        r'sogou',
        r'mj12bot',
        r'uptimerobot',
        r'pingdom',
    ]

    # مسیرهای استاتیک برای عدم ثبت
    SKIP_PATHS = [
        r'^/static/',
        r'^/media/',
        r'^/favicon\.ico$',
        r'^/robots\.txt$',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

        # کامپایل الگوهای ربات
        self.bot_patterns = [re.compile(p, re.I) for p in self.BOT_PATTERNS]
        self.skip_patterns = [re.compile(p) for p in self.SKIP_PATHS]

        # تنظیمات کش
        self.cache_timeout = getattr(settings, 'VISIT_CACHE_TIMEOUT', 3600)
        self.visit_interval = getattr(settings, 'VISIT_INTERVAL_MINUTES', 60)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # ثبت بازدید قبل از پردازش درخواست
        if not self.should_skip(request):
            self.record_visit(request)

        response = self.get_response(request)
        return response

    def should_skip(self, request: HttpRequest) -> bool:
        """بررسی اینکه آیا این درخواست باید ثبت شود؟"""

        # رد کردن درخواست‌های مدیریتی و API
        if request.path.startswith('/admin/') or request.path.startswith('/api/'):
            return True

        # رد کردن مسیرهای استاتیک
        for pattern in self.skip_patterns:
            if pattern.match(request.path):
                return True

        # رد کردن درخواست‌های AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return True

        return False

    def is_bot(self, user_agent: str) -> bool:
        """تشخیص ربات بودن بر اساس User-Agent"""
        if not user_agent:
            return False

        for pattern in self.bot_patterns:
            if pattern.search(user_agent):
                return True

        return False

    def get_ip(self, request: HttpRequest) -> str:
        """دریافت IP واقعی کاربر با بررسی هدرهای مختلف"""

        # بررسی هدرهای معتبر
        headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CF_CONNECTING_IP',  # Cloudflare
            'HTTP_X_CLUSTER_CLIENT_IP',
        ]

        for header in headers:
            ip = request.META.get(header)
            if ip:
                # در X-Forwarded-For ممکن است چندین IP باشد
                ips = ip.split(',')
                for ip in ips:
                    ip = ip.strip()
                    if ip and ip != 'unknown':
                        return ip

        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def get_visit_key(self, ip: str, path: str) -> str:
        """ایجاد کلید کش برای جلوگیری از ثبت تکراری"""
        return f"visit:{ip}:{path}"

    def record_visit(self, request: HttpRequest) -> Optional[Visit]:
        """ثبت بازدید با استفاده از کش برای بهینه‌سازی"""

        try:
            ip = self.get_ip(request)
            path = request.path[:255]
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            referer = request.META.get('HTTP_REFERER', '')[:500]
            method = request.method

            # تشخیص ربات
            is_bot = self.is_bot(user_agent)

            # کلید کش برای جلوگیری از ثبت تکراری
            cache_key = self.get_visit_key(ip, path)

            # بررسی وجود در کش
            if cache.get(cache_key):
                # به‌روزرسانی last_seen برای بازدیدهای قبلی
                try:
                    visit = Visit.objects.filter(ip=ip, path=path).latest('created_at')
                    if visit:
                        # افزایش تعداد بازدید
                        Visit.objects.filter(pk=visit.pk).update(
                            visit_count=models.F('visit_count') + 1,
                            last_seen=timezone.now()
                        )
                except Visit.DoesNotExist:
                    pass
                return None

            # ثبت بازدید جدید
            visit = Visit.objects.create(
                ip=ip,
                path=path,
                method=method,
                user_agent=user_agent,
                referer=referer,
                is_bot=is_bot,
                visit_count=1,
            )

            # ذخیره در کش برای جلوگیری از ثبت تکراری
            cache.set(
                cache_key,
                visit.pk,
                timeout=self.cache_timeout
            )

            # حذف کش‌های قدیمی در صورت زیاد شدن
            if Visit.objects.count() % 1000 == 0:
                self.cleanup_old_visits()

            return visit

        except Exception as e:
            logger.exception(f"Failed to save visit: {e}")
            return None

    def cleanup_old_visits(self, days: int = 90):
        """پاکسازی بازدیدهای قدیمی"""
        try:
            threshold = timezone.now() - timedelta(days=days)
            deleted_count, _ = Visit.objects.filter(
                created_at__lt=threshold
            ).delete()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old visits")

        except Exception as e:
            logger.exception(f"Failed to cleanup old visits: {e}")