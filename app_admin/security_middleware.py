
import ipaddress

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from .models import SecurityIPRule


def security_blocked_response(request, reason="ip"):
    """
    Render the existing Persian security-blocked page.
    """
    return render(
        request,
        "admin/security/access_blocked.html",
        {"reason": reason},
        status=403,
    )


def axes_lockout_response(request, *args, **kwargs):
    """
    Custom lockout response for django-axes.
    """
    return security_blocked_response(
        request,
        reason="axes",
    )


class AdminIPSecurityMiddleware:
    """
    Production admin IP protection.

    - Explicit block rules always take priority.
    - Optional allowlist limits /admin/ to approved IPs.
    - In development, both controls can be disabled.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        blocking_enabled = getattr(
            settings,
            "ADMIN_IP_BLOCKING_ENABLED",
            False,
        )

        allowlist_enabled = getattr(
            settings,
            "ADMIN_IP_ALLOWLIST_ENABLED",
            False,
        )

        if not blocking_enabled and not allowlist_enabled:
            return self.get_response(request)

        path = request.path_info

        if not (
            path == "/admin"
            or path.startswith("/admin/")
        ):
            return self.get_response(request)

        raw_ip = request.META.get(
            "REMOTE_ADDR",
            "",
        )

        try:
            client_ip = str(
                ipaddress.ip_address(raw_ip)
            )
        except (ValueError, TypeError):
            # Never bypass an enabled allowlist when
            # the client IP cannot be determined.
            if allowlist_enabled:
                return security_blocked_response(
                    request,
                    reason="ip",
                )

            return self.get_response(request)

        now = timezone.now()

        effective_rules = SecurityIPRule.objects.filter(
            ip_address=client_ip,
            is_active=True,
        ).filter(
            Q(expires_at__isnull=True)
            | Q(expires_at__gt=now)
        )

        # Explicit blocks have priority.
        if blocking_enabled:
            is_blocked = effective_rules.filter(
                rule_type="block",
            ).exists()

            if is_blocked:
                return security_blocked_response(
                    request,
                    reason="ip",
                )

        # In allowlist mode, every admin request
        # must originate from an approved IP.
        if allowlist_enabled:
            is_allowed = effective_rules.filter(
                rule_type="allow",
            ).exists()

            if not is_allowed:
                return security_blocked_response(
                    request,
                    reason="ip",
                )

        return self.get_response(request)
