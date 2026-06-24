from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.template.response import TemplateResponse
import jdatetime

from .models import SecurityContact


@admin.register(SecurityContact)
class SecurityContactAdmin(admin.ModelAdmin):

    # ---------- PERMISSIONS ----------
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True  # ✅ اجازه حذف فعال شد

    # ---------- ACTIONS ----------
    actions = ["delete_selected"]  # ✅ حذف گروهی

    # ---------- JALALI DATE ----------
    def created_at_short(self, obj):
        if not obj.created_at:
            return "—"
        j_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return j_date.strftime("%Y/%m/%d %H:%M")

    created_at_short.short_description = "تاریخ ارسال (شمسی)"

    # ---------- LIST ----------
    list_display = (
        "full_name",
        "phone",
        "subject",
        "print_button",
        "created_at_short",
    )

    search_fields = ("first_name", "last_name", "phone", "subject", "message")
    ordering = ("-created_at",)

    # ---------- READ ONLY ----------
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields] + [
            "created_at_short",
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
            "fields": ("subject", "message"),
        }),
        ("ℹ️ اطلاعات سیستمی", {
            "fields": ("created_at_short",),
            "classes": ("collapse",),
        }),
    )

    # ---------- فقط پیام‌های جدید ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match and request.resolver_match.url_name == "changelist":
            return qs.filter(status="new")
        return qs

    # ---------- HELPERS ----------
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "نام و نام خانوادگی"

    # ---------- CUSTOM PRINT URL ----------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/print/",
                self.admin_site.admin_view(self.print_view),
                name="security_contact_print",
            ),
        ]
        return custom_urls + urls

    # ---------- PRINT BUTTON ----------
    def print_button(self, obj):
        url = reverse("admin:security_contact_print", args=[obj.pk])
        return format_html(
            "<a href='{}' target='_blank' "
            "style='background:#4caf50;color:white;padding:6px 12px;"
            "border-radius:8px;text-decoration:none;font-weight:bold;'>"
            "🖨 گزارش</a>",
            url
        )

    print_button.short_description = "پرینت گزارش"

    # ---------- PRINT VIEW ----------
    def print_view(self, request, pk):
        contact = SecurityContact.objects.get(pk=pk)
        return TemplateResponse(
            request,
            "RTL/print/security_print.html",
            {"contact": contact},
        )
