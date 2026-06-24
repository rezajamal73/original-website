from django.contrib import admin
from django.utils.html import format_html

from .models import CompanyCatalog


@admin.register(CompanyCatalog)
class CompanyCatalogAdmin(admin.ModelAdmin):
    actions = None  # ❌ حذف bulk actions

    # ================================
    # List View
    # ================================
    list_display = (
        "title",
        "updated_at_jalali_display",
        "updated_at_gregorian_display",
    )

    ordering = ("-updated_at",)
    search_fields = ("title",)

    readonly_fields = (
        "updated_at",
        "updated_at_jalali_display",
        "updated_at_gregorian_display",
    )

    # ================================
    # Form Layout
    # ================================
    fieldsets = (
        ("📘 اطلاعات کاتالوگ", {
            "fields": ("title", "description", "pdf_file"),
        }),
        ("🕒 بروزرسانی", {
            "fields": (
                "updated_at",
                "updated_at_jalali_display",
                "updated_at_gregorian_display",
            ),
        }),
    )

    # ================================
    # Single Object Restriction
    # ================================
    def has_add_permission(self, request):
        """
        Allow adding only ONE catalog instance
        """
        if CompanyCatalog.objects.exists():
            return False
        return super().has_add_permission(request)

    # ================================
    # Custom Columns
    # ================================
    def updated_at_jalali_display(self, obj):
        return format_html(
            "<strong>{}</strong>",
            obj.updated_at_jalali
        )

    updated_at_jalali_display.short_description = "آخرین بروزرسانی (شمسی)"

    def updated_at_gregorian_display(self, obj):
        return obj.updated_at_gregorian

    updated_at_gregorian_display.short_description = "آخرین بروزرسانی (میلادی)"
