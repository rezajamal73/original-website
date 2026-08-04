from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    # ---------- READ ONLY ----------
    def has_add_permission(self, request):
        return False

    # فقط اجازه مشاهده (فیلدها همچنان readonly هستند)
    def has_change_permission(self, request, obj=None):
        return True

    # ---------- LIST ----------
    list_display = (
        "full_name",
        "phone",
        "email",
        "subject",
        "status_badge",
        "print_button",
        "created_at_fa",
    )

    list_filter = ("status",)

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "subject",
        "message",
    )

    ordering = ("-created_at",)

    # ---------- READONLY FIELDS ----------
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields] + [
            "created_at_fa",
            "full_name",
        ]

    # ---------- FIELDSETS ----------
    fieldsets = (
        ("👤 اطلاعات فرستنده", {
            "fields": (
                ("first_name", "last_name"),
                "phone",
                "email",
            ),
        }),
        ("📝 متن پیام", {
            "fields": (
                "subject",
                "message",
            ),
        }),
        ("ℹ️ اطلاعات سیستمی", {
            "fields": (
                "status",
                "created_at_fa",
            ),
            "classes": ("collapse",),
        }),
    )

    # ---------- فقط پیام‌های جدید ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match and request.resolver_match.url_name == "changelist":
            return qs.filter(status="new")
        return qs

    # ---------- هنگام باز کردن پیام ----------
    def change_view(self, request, object_id, form_url="", extra_context=None):
        contact = self.get_object(request, object_id)

        if contact and contact.status == "new":
            contact.status = "seen"
            contact.save(update_fields=["status"])

        extra_context = extra_context or {}
        extra_context["show_save"] = False
        extra_context["show_save_and_continue"] = False
        extra_context["show_save_and_add_another"] = False

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    # ---------- STATUS BADGE ----------
    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        if obj.status == "new":
            return mark_safe(
                '<span style="background:#dc3545;color:white;'
                'padding:4px 12px;border-radius:14px;font-size:12px;">'
                'جدید</span>'
            )

        return mark_safe(
            '<span style="background:#198754;color:white;'
            'padding:4px 12px;border-radius:14px;font-size:12px;">'
            'دیده شده</span>'
        )

    # ---------- PRINT URL ----------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/print/",
                self.admin_site.admin_view(self.print_view),
                name="contactmessage_print",
            ),
        ]
        return custom_urls + urls

    # ---------- PRINT BUTTON ----------
    @admin.display(description="پرینت")
    def print_button(self, obj):
        url = reverse("admin:contactmessage_print", args=[obj.pk])
        return format_html(
            "<a href='{}' target='_blank' "
            "style='background:#4caf50;color:white;padding:6px 12px;"
            "border-radius:8px;text-decoration:none;font-weight:bold;'>"
            "🖨 گزارش</a>",
            url,
        )

    # ---------- PRINT VIEW ----------
    def print_view(self, request, pk):
        contact = get_object_or_404(ContactMessage, pk=pk)

        if contact.status == "new":
            contact.status = "seen"
            contact.save(update_fields=["status"])

        return TemplateResponse(
            request,
            "RTL/print/contact_print.html",
            {
                "contact": contact,
            },
        )