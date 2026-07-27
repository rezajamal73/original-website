import logging
import re
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.urls import resolve, Resolver404
from django.utils import timezone

from .models import Visit

logger = logging.getLogger(__name__)


class VisitMiddleware:
    """ثبت بازدید کاربران"""

    BOT_PATTERNS = [
        r"bot",
        r"crawler",
        r"spider",
        r"googlebot",
        r"bingbot",
        r"slurp",
        r"duckduckbot",
        r"baiduspider",
        r"yandexbot",
        r"facebookexternalhit",
        r"twitterbot",
        r"linkedinbot",
        r"pinterestbot",
        r"semrushbot",
        r"ahrefsbot",
        r"majestic",
        r"rogerbot",
        r"exabot",
        r"uptimerobot",
        r"pingdom",
        r"curl",
        r"wget",
        r"python",
        r"aiohttp",
        r"headless",
    ]

    SKIP_PATHS = (
        r"^/static/",
        r"^/media/",
        r"^/favicon\.ico$",
        r"^/robots\.txt$",
    )

    def __init__(self, get_response):
        self.get_response = get_response

        self.bot_patterns = [re.compile(p, re.I) for p in self.BOT_PATTERNS]
        self.skip_patterns = [re.compile(p) for p in self.SKIP_PATHS]

        self.visit_interval = getattr(
            settings,
            "VISIT_INTERVAL_MINUTES",
            60,
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:

        if not self.should_skip(request):
            self.record_visit(request)

        return self.get_response(request)

    def should_skip(self, request) -> bool:

        path = request.path

        if path.startswith("/admin/"):
            return True

        if path.startswith("/api/"):
            return True

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True

        return any(p.match(path) for p in self.skip_patterns)

    def is_bot(self, user_agent: str) -> bool:

        if not user_agent:
            return False

        return any(p.search(user_agent) for p in self.bot_patterns)

    def get_ip(self, request) -> str:

        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded:
            return forwarded.split(",")[0].strip()

        return (
            request.META.get("HTTP_X_REAL_IP")
            or request.META.get("HTTP_CF_CONNECTING_IP")
            or request.META.get("REMOTE_ADDR")
            or "0.0.0.0"
        )

    def get_visit_key(self, ip: str, path: str) -> str:
        return f"visit:{ip}:{path}"

    def get_page_name(self, path: str) -> str:
        """
        تبدیل مسیر به نام صفحه
        """

        try:
            match = resolve(path)

            if match.url_name:
                return match.url_name.replace("_", " ").title()

            return path

        except Resolver404:
            return path

    def record_visit(self, request) -> Optional[Visit]:

        try:

            ip = self.get_ip(request)
            path = request.path[:255]

            cache_key = self.get_visit_key(ip, path)

            if cache.get(cache_key):

                visit = (
                    Visit.objects.filter(
                        ip=ip,
                        path=path,
                    )
                    .only("id")
                    .order_by("-created_at")
                    .first()
                )

                if visit:
                    Visit.objects.filter(pk=visit.pk).update(
                        visit_count=F("visit_count") + 1,
                        last_seen=timezone.now(),
                    )

                return visit

            Visit.objects.create(
                ip=ip,
                path=path,
                method=request.method,
                user_agent=request.META.get(
                    "HTTP_USER_AGENT",
                    "",
                )[:500],
                referer=request.META.get(
                    "HTTP_REFERER",
                    "",
                )[:500],
                is_bot=self.is_bot(
                    request.META.get(
                        "HTTP_USER_AGENT",
                        "",
                    )
                ),
            )

            cache.set(
                cache_key,
                True,
                timeout=self.visit_interval * 60,
            )

            if Visit.objects.count() % 1000 == 0:
                self.cleanup_old_visits()

        except Exception:
            logger.exception("Visit middleware error")

        return None

    def cleanup_old_visits(self, days=90):

        try:

            Visit.objects.filter(
                created_at__lt=timezone.now() - timedelta(days=days)
            ).delete()

        except Exception:
            logger.exception("Visit cleanup error")