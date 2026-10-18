
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    SecurityIPRule,
    AllowedIP,
    SecurityAuditLog,
)


# ==========================================
# Superuser Permissions
# ==========================================

class SuperuserOnlyAdmin:

    def _is_superuser(self, request):
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )

    def has_module_permission(self, request):
        return self._is_superuser(request)

    def has_view_permission(self, request, obj=None):
        return self._is_superuser(request)

    def has_add_permission(self, request):
        return self._is_superuser(request)

    def has_change_permission(self, request, obj=None):
        return self._is_superuser(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_superuser(request)


# ==========================================
# Reusable Single Delete Button
# ==========================================

class SingleDeleteButtonMixin:

    @admin.display(description="حذف")
    def delete_button(self, obj):
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


# ==========================================
# IP Address Rule Form
# ==========================================

class IPAddressRuleForm(forms.ModelForm):

    class Meta:
        model = SecurityIPRule

        fields = (
            "ip_address",
            "description",
            "expires_at",
            "is_active",
        )

    def clean_ip_address(self):
        ip = self.cleaned_data["ip_address"]

        return (
            ip.strip()
            if isinstance(ip, str)
            else ip
        )

    def clean(self):
        cleaned = super().clean()

        expires_at = cleaned.get("expires_at")

        if (
            expires_at is not None
            and expires_at <= timezone.now()
            and cleaned.get("is_active", True)
        ):
            self.add_error(
                "expires_at",
                "تاریخ انقضا باید در آینده باشد.",
            )

        return cleaned


# ==========================================
# IP Admin Base
# ==========================================

class IPAdminBase(
    SingleDeleteButtonMixin,
    SuperuserOnlyAdmin,
    admin.ModelAdmin,
):

    form = IPAddressRuleForm

    list_display = (
        "ip_address",
        "description",
        "is_active",
        "effective_status",
        "expires_at",
        "created_by",
        "created_at",
        "delete_button",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "ip_address",
        "description",
    )

    readonly_fields = (
        "created_by",
        "created_at",
    )

    fields = (
        "ip_address",
        "description",
        "expires_at",
        "is_active",
        "created_by",
        "created_at",
    )

    list_per_page = 30

    actions = ["delete_selected"]

    rule_type_value = None
    rule_label = "IP"

    # --------------------------------------
    # Filter Rules
    # --------------------------------------

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                rule_type=self.rule_type_value
            )
        )

    # --------------------------------------
    # Effective Status
    # --------------------------------------

    @admin.display(description="وضعیت واقعی")
    def effective_status(self, obj):

        if not obj.is_active:
            return "غیرفعال"

        if (
            obj.expires_at is not None
            and obj.expires_at <= timezone.now()
        ):
            return "منقضی‌شده"

        return "فعال"

    # --------------------------------------
    # Save + Audit Log
    # --------------------------------------

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        if not self.has_change_permission(request):
            raise PermissionDenied

        old_values = None

        if change:
            old = (
                self.get_queryset(request)
                .get(pk=obj.pk)
            )

            old_values = (
                f"IP={old.ip_address}, "
                f"type={old.rule_type}, "
                f"active={old.is_active}, "
                f"expires={old.expires_at}"
            )
        else:
            obj.created_by = request.user

        obj.rule_type = self.rule_type_value

        with transaction.atomic():

            super().save_model(
                request,
                obj,
                form,
                change,
            )

            SecurityAuditLog.objects.create(
                action=(
                    f"ویرایش {self.rule_label}"
                    if change
                    else f"افزودن {self.rule_label}"
                ),
                ip_address=obj.ip_address,
                performed_by=request.user,
                details=(
                    f"شناسه قانون: {obj.pk}\n"
                    f"مقادیر قبلی: {old_values}\n"
                    f"IP: {obj.ip_address}\n"
                    f"نوع: {obj.rule_type}\n"
                    f"فعال: {obj.is_active}\n"
                    f"انقضا: {obj.expires_at}"
                ),
            )

    # --------------------------------------
    # Single Delete + Audit Log
    # --------------------------------------

    def delete_model(self, request, obj):

        if not self.has_delete_permission(
            request,
            obj,
        ):
            raise PermissionDenied

        with transaction.atomic():

            SecurityAuditLog.objects.create(
                action=f"حذف {self.rule_label}",
                ip_address=obj.ip_address,
                performed_by=request.user,
                details=(
                    f"شناسه قانون: {obj.pk}\n"
                    f"نوع: {obj.rule_type}\n"
                    f"توضیحات: {obj.description}"
                ),
            )

            super().delete_model(
                request,
                obj,
            )

    # --------------------------------------
    # Bulk Delete + Audit Log
    # --------------------------------------

    def delete_queryset(
        self,
        request,
        queryset,
    ):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        with transaction.atomic():

            for obj in queryset.iterator():
                self.delete_model(
                    request,
                    obj,
                )


# ==========================================
# Blocked IP Admin
# ==========================================

@admin.register(SecurityIPRule)
class SecurityIPRuleAdmin(IPAdminBase):

    rule_type_value = "block"
    rule_label = "IP غیرمجاز"


# ==========================================
# Allowed IP Admin
# ==========================================

@admin.register(AllowedIP)
class AllowedIPAdmin(IPAdminBase):

    rule_type_value = "allow"
    rule_label = "IP مجاز"


# ==========================================
# Security Audit Log Admin
# ==========================================

@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(
    SingleDeleteButtonMixin,
    SuperuserOnlyAdmin,
    admin.ModelAdmin,
):

    list_display = (
        "action",
        "ip_address",
        "performed_by",
        "created_at",
        "delete_button",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "action",
        "ip_address",
        "details",
    )

    readonly_fields = (
        "action",
        "ip_address",
        "details",
        "performed_by",
        "created_at",
    )

    list_per_page = 50

    actions = ["delete_selected"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return self._is_superuser(request)

    def delete_model(self, request, obj):
        if not self.has_delete_permission(
            request,
            obj,
        ):
            raise PermissionDenied

        super().delete_model(request, obj)

    def delete_queryset(
        self,
        request,
        queryset,
    ):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        with transaction.atomic():
            super().delete_queryset(
                request,
                queryset,
            )


# ==========================================
# Register Axes Admin
# ==========================================

from .axes_admin import register_secure_axes_admin

register_secure_axes_admin()
