
import ipaddress
import logging
import re
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import Visit
from .device_detector import DeviceDetector

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
        r"masscan",
        r"nmap",
        r"nikto",
        r"sqlmap",
        r"acunetix",
        r"nessus",
        r"dirbuster",
        r"gobuster",
        r"wfuzz",
    ]

    SKIP_PATHS = (
        r"^/static/",
        r"^/media/",
        r"^/favicon\.ico$",
        r"^/robots\.txt$",
        r"^/sitemap\.xml$",
        r"^/captcha/",
        r"^/admin",
        r"^/__debug__/",
        r"^/health",
        r"^/metrics",
        r"^/wp-",
        r"^/xmlrpc\.php",
        r"^/\.env",
        r"^/\.git",
    )

    def __init__(self, get_response):
        self.get_response = get_response

        self.bot_patterns = [
            re.compile(p, re.I)
            for p in self.BOT_PATTERNS
        ]

        self.skip_patterns = [
            re.compile(p)
            for p in self.SKIP_PATHS
        ]

        self.visit_interval = getattr(
            settings,
            "VISIT_INTERVAL_MINUTES",
            60,
        )

    def __call__(
        self,
        request: HttpRequest
    ) -> HttpResponse:

        if not self.should_skip(request):
            self.record_visit(request)

        return self.get_response(request)

    def should_skip(self, request) -> bool:

        path = request.path

        if path == "/admin" or path.startswith("/admin/"):
            return True

        if path.startswith("/api/"):
            return True

        if hasattr(request, "user"):
            if request.user.is_authenticated:
                if (
                    request.user.is_staff
                    or request.user.is_superuser
                ):
                    return True

        if (
            request.headers.get("X-Requested-With")
            == "XMLHttpRequest"
        ):
            return True

        return any(
            p.match(path)
            for p in self.skip_patterns
        )

    def is_bot(self, user_agent: str) -> bool:

        if not user_agent:
            return False

        return any(
            p.search(user_agent)
            for p in self.bot_patterns
        )

    def _valid_ip(self, ip: str) -> bool:

        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def get_ip(self, request) -> str:
        """
        اعتماد به هدرهای IP فقط از پروکسی معتبر.
        """

        peer = (
            request.META.get("REMOTE_ADDR") or ""
        ).strip()

        if not self._valid_ip(peer):
            return "0.0.0.0"

        trusted = set(
            getattr(
                settings,
                "VISIT_TRUSTED_PROXIES",
                (),
            )
        )

        if peer not in trusted:
            return peer

        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR",
            "",
        )

        chain = [
            part.strip()
            for part in forwarded.split(",")
            if part.strip()
        ]

        if not chain:
            return peer

        if any(
            not self._valid_ip(ip)
            for ip in chain
        ):
            return peer

        for ip in reversed(chain):
            if ip not in trusted:
                return ip

        return chain[0]

    def get_visit_key(self, ip, path):
        return f"visit:{ip}:{path}"

    def record_visit(
        self,
        request
    ) -> Optional[Visit]:

        try:
            ip = self.get_ip(request)
            path = request.path[:255]

            user_agent = request.META.get(
                "HTTP_USER_AGENT",
                "",
            )

            is_bot = self.is_bot(user_agent)

            cache_key = self.get_visit_key(
                ip,
                path,
            )

            device_info = DeviceDetector.detect_all(
                user_agent,
                is_bot,
            )

            if cache.get(cache_key):
                Visit.objects.filter(
                    ip=ip,
                    path=path,
                ).update(
                    last_seen=timezone.now()
                )
                return None

            visit, created = Visit.objects.get_or_create(
                ip=ip,
                path=path,
                defaults={
                    "method": request.method,
                    "user_agent": user_agent[:500],
                    "referer": request.META.get(
                        "HTTP_REFERER", ""
                    )[:500],
                    "is_bot": is_bot,
                    "device_type": device_info["device_type"],
                    "os": device_info["os"],
                    "browser": device_info["browser"],
                    "device_model": device_info[
                        "device_model"
                    ][:100],
                    "language": request.META.get(
                        "HTTP_ACCEPT_LANGUAGE", ""
                    )[:10],
                },
            )

            if not created:
                Visit.objects.filter(
                    pk=visit.pk
                ).update(
                    last_seen=timezone.now(),
                    method=request.method,
                    user_agent=user_agent[:500],
                    referer=request.META.get(
                        "HTTP_REFERER", ""
                    )[:500],
                    visit_count=F("visit_count") + 1,
                    device_type=device_info["device_type"],
                    os=device_info["os"],
                    browser=device_info["browser"],
                    device_model=device_info[
                        "device_model"
                    ][:100],
                )

            cache.set(
                cache_key,
                True,
                timeout=self.visit_interval * 60,
            )

            if Visit.objects.count() % 1000 == 0:
                self.cleanup_old_visits()

            return visit

        except Exception:
            logger.exception(
                "Visit middleware error"
            )
            return None

    def cleanup_old_visits(self, days=90):

        try:
            Visit.objects.filter(
                created_at__lt=(
                    timezone.now()
                    - timedelta(days=days)
                )
            ).delete()

        except Exception:
            logger.exception(
                "Visit cleanup error"
            )
