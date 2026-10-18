
import ipaddress
import jdatetime

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from axes.admin import (
    AccessAttemptAdmin,
    AccessLogAdmin,
    AccessFailureLogAdmin,
)
from axes.models import (
    AccessAttempt,
    AccessLog,
    AccessFailureLog,
)

from .models import SecurityIPRule, SecurityAuditLog


# ==========================================
# Persian Date
# ==========================================

def persian_datetime(value):
    if not value:
        return "—"

    if timezone.is_aware(value):
        value = timezone.localtime(value)

    jalali = jdatetime.datetime.fromgregorian(
        datetime=value
    )

    return jalali.strftime("%Y/%m/%d - %H:%M")


# ==========================================
# Security Actions Mixin
# ==========================================

class SecurityActionsMixin:

    # --------------------------------------
    # Permissions
    # --------------------------------------

    def has_module_permission(self, request):
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

    # --------------------------------------
    # Single + Bulk Delete
    # --------------------------------------

    def get_actions(self, request):
        actions = super().get_actions(request)

        if self.has_delete_permission(request):
            actions["delete_selected"] = (
                admin.actions.delete_selected,
                "delete_selected",
                "🗑 حذف گروهی موارد انتخاب‌شده",
            )
        else:
            actions.pop("delete_selected", None)

        return actions

    def delete_queryset(self, request, queryset):
        if not self.has_delete_permission(request):
            raise PermissionDenied(
                "شما مجوز حذف این گزارش‌ها را ندارید."
            )

        with transaction.atomic():
            queryset.delete()

    def delete_model(self, request, obj):
        if not self.has_delete_permission(request, obj):
            raise PermissionDenied(
                "شما مجوز حذف این گزارش را ندارید."
            )

        with transaction.atomic():
            obj.delete()

    # --------------------------------------
    # List Display
    # --------------------------------------

    def get_list_display(self, request):
        columns = list(
            super().get_list_display(request)
        )

        date_columns = {
            "attempt_time",
            "logout_time",
            "attempt_time_display",
            "logout_time_display",
        }

        columns = [
            column
            for column in columns
            if column not in date_columns
        ]

        if "jalali_attempt_time" not in columns:
            columns.insert(
                0,
                "jalali_attempt_time",
            )

        if self.model is AccessLog:
            if "jalali_logout_time" not in columns:
                columns.insert(
                    1,
                    "jalali_logout_time",
                )

        if "security_ip_action" not in columns:
            columns.append(
                "security_ip_action"
            )

        if "delete_record_link" not in columns:
            columns.append(
                "delete_record_link"
            )

        return columns

    # --------------------------------------
    # Jalali Dates
    # --------------------------------------

    @admin.display(
        description="زمان ورود / تلاش (شمسی)",
        ordering="attempt_time",
    )
    def jalali_attempt_time(self, obj):
        return persian_datetime(
            getattr(
                obj,
                "attempt_time",
                None,
            )
        )

    @admin.display(
        description="زمان خروج (شمسی)",
        ordering="logout_time",
    )
    def jalali_logout_time(self, obj):
        return persian_datetime(
            getattr(
                obj,
                "logout_time",
                None,
            )
        )

    # --------------------------------------
    # Single Delete Button
    # --------------------------------------

    @admin.display(description="حذف")
    def delete_record_link(self, obj):
        url = reverse(
            (
                f"admin:{obj._meta.app_label}_"
                f"{obj._meta.model_name}_delete"
            ),
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}" style="'
            'display:inline-block;'
            'background:#c62828;'
            'color:#ffffff;'
            'padding:5px 12px;'
            'border-radius:6px;'
            'text-decoration:none;'
            'font-weight:bold;">'
            '🗑 حذف'
            '</a>',
            url,
        )

    # --------------------------------------
    # IP Block Status
    # --------------------------------------

    def _is_blocked(self, ip):
        now = timezone.now()

        return SecurityIPRule.objects.filter(
            ip_address=ip,
            rule_type="block",
            is_active=True,
        ).filter(
            Q(expires_at__isnull=True)
            | Q(expires_at__gt=now)
        ).exists()

    @admin.display(
        description="کنترل امنیت IP"
    )
    def security_ip_action(self, obj):
        if not obj.ip_address:
            return "IP نامشخص"

        blocked = self._is_blocked(
            obj.ip_address
        )

        action = (
            "unblock"
            if blocked
            else "block"
        )

        label = (
            "رفع مسدودی"
            if blocked
            else "مسدود کردن"
        )

        url = reverse(
            (
                f"admin:{obj._meta.app_label}_"
                f"{obj._meta.model_name}_security_ip"
            ),
            args=[
                obj.pk,
                action,
            ],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            label,
        )

    # --------------------------------------
    # Custom URLs
    # --------------------------------------

    def get_urls(self):
        custom_urls = [
            path(
                "<int:object_id>/security-ip/<str:action>/",
                self.admin_site.admin_view(
                    self.change_ip_status
                ),
                name=(
                    f"{self.model._meta.app_label}_"
                    f"{self.model._meta.model_name}_security_ip"
                ),
            ),
        ]

        return (
            custom_urls
            + super().get_urls()
        )

    # --------------------------------------
    # Block / Unblock IP
    # --------------------------------------

    def change_ip_status(
        self,
        request,
        object_id,
        action,
    ):
        if not self.has_module_permission(request):
            raise PermissionDenied

        if action not in (
            "block",
            "unblock",
        ):
            raise PermissionDenied

        obj = self.get_object(
            request,
            object_id,
        )

        if obj is None or not obj.ip_address:
            raise PermissionDenied

        try:
            target_ip = str(
                ipaddress.ip_address(
                    obj.ip_address
                )
            )
        except ValueError:
            raise PermissionDenied

        current_ip = request.META.get(
            "REMOTE_ADDR",
            "",
        )

        if (
            action == "block"
            and target_ip == current_ip
        ):
            self.message_user(
                request,
                (
                    "برای جلوگیری از قطع دسترسی، "
                    "مسدودسازی IP فعلی شما مجاز نیست."
                ),
                messages.ERROR,
            )

            return redirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_"
                    f"{self.model._meta.model_name}_changelist"
                )
            )

        changelist_url = reverse(
            f"admin:{self.model._meta.app_label}_"
            f"{self.model._meta.model_name}_changelist"
        )

        if request.method == "GET":
            context = {
                **self.admin_site.each_context(
                    request
                ),
                "title": "تأیید عملیات امنیتی",
                "target_ip": target_ip,
                "operation": (
                    "مسدودسازی"
                    if action == "block"
                    else "رفع مسدودی"
                ),
                "action_url": request.path,
                "back_url": changelist_url,
            }

            return TemplateResponse(
                request,
                "admin/security/confirm_ip_action.html",
                context,
            )

        if request.method != "POST":
            return HttpResponse(
                status=405
            )

        # ----------------------------------
        # Apply IP Action
        # ----------------------------------

        with transaction.atomic():

            if action == "block":

                existing = (
                    SecurityIPRule.objects
                    .select_for_update()
                    .filter(
                        ip_address=target_ip,
                        rule_type="block",
                    )
                    .order_by("pk")
                )

                first_rule = existing.first()

                if first_rule:

                    existing.exclude(
                        pk=first_rule.pk
                    ).update(
                        is_active=False
                    )

                    first_rule.is_active = True
                    first_rule.expires_at = None
                    first_rule.description = (
                        "مسدودسازی از گزارش Axes"
                    )
                    first_rule.created_by = request.user

                    first_rule.save()

                else:

                    SecurityIPRule.objects.create(
                        ip_address=target_ip,
                        rule_type="block",
                        is_active=True,
                        expires_at=None,
                        description=(
                            "مسدودسازی از گزارش Axes"
                        ),
                        created_by=request.user,
                    )

                operation = (
                    "مسدودسازی IP از Axes"
                )

            else:

                SecurityIPRule.objects.filter(
                    ip_address=target_ip,
                    rule_type="block",
                    is_active=True,
                ).update(
                    is_active=False
                )

                operation = (
                    "رفع مسدودی IP از Axes"
                )

            # ----------------------------------
            # Audit Log
            # ----------------------------------

            SecurityAuditLog.objects.create(
                action=operation,
                ip_address=target_ip,
                performed_by=request.user,
                details=(
                    f"مدل: {obj._meta.label}\n"
                    f"شناسه گزارش: {obj.pk}"
                ),
            )

        self.message_user(
            request,
            f"عملیات برای IP {target_ip} انجام شد.",
            messages.SUCCESS,
        )

        return redirect(
            changelist_url
        )


# ==========================================
# Access Attempt Admin
# ==========================================

class SecureAccessAttemptAdmin(
    SecurityActionsMixin,
    AccessAttemptAdmin,
):
    pass


# ==========================================
# Access Log Admin
# ==========================================

class SecureAccessLogAdmin(
    SecurityActionsMixin,
    AccessLogAdmin,
):
    pass


# ==========================================
# Access Failure Log Admin
# ==========================================

class SecureAccessFailureLogAdmin(
    SecurityActionsMixin,
    AccessFailureLogAdmin,
):
    pass


# ==========================================
# Register Secure Axes Admin
# ==========================================

def register_secure_axes_admin():

    registrations = (
        (
            AccessAttempt,
            SecureAccessAttemptAdmin,
        ),
        (
            AccessLog,
            SecureAccessLogAdmin,
        ),
        (
            AccessFailureLog,
            SecureAccessFailureLogAdmin,
        ),
    )

    for model, admin_class in registrations:

        if model in admin.site._registry:
            admin.site.unregister(
                model
            )

        admin.site.register(
            model,
            admin_class,
        )
