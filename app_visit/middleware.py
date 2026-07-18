import logging
from datetime import timedelta

from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import Visit

logger = logging.getLogger(__name__)


class VisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            ip = self.get_ip(request)

            one_hour_ago = timezone.now() - timedelta(hours=1)

            exists = Visit.objects.filter(
                ip=ip,
                created_at__gte=one_hour_ago,
            ).exists()

            if not exists:
                Visit.objects.create(
                    ip=ip,
                    path=request.path[:255],
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                )

        except Exception:
            logger.exception("Failed to save visit.")

        return self.get_response(request)

    @staticmethod
    def get_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
            if ip:
                return ip

        real_ip = request.META.get("HTTP_X_REAL_IP")
        if real_ip:
            return real_ip.strip()

        return request.META.get("REMOTE_ADDR", "0.0.0.0")