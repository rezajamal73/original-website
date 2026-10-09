from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import CompanyCatalog


# ---------------------------------------
#   GLOBAL ACTION BUTTONS (EDIT + DELETE)
# ---------------------------------------
def admin_action_buttons(obj):
    edit_url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.pk],
    )
    delete_url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        """
        <div style="display:inline-flex; gap:6px; align-items:center;">
            <a href="{}"
               style="
                    background:#1e88e5;
                    color:white;
                    padding:6px 10px;
                    border-radius:8px;
                    text-decoration:none;
                    font-weight:bold;
                    white-space:nowrap;
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);
                    display:inline-flex;
                    align-items:center;
                    gap:5px;
               ">
                ✏️
            </a>
            <a href="{}"
               style="
                    background:#d7263d;
                    color:white;
                    padding:6px 10px;
                    border-radius:8px;
                    text-decoration:none;
                    font-weight:bold;
                    white-space:nowrap;
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);
                    display:inline-flex;
                    align-items:center;
                    gap:5px;
               ">
                🗑
            </a>
        </div>
        """,
        edit_url,
        delete_url,
    )


admin_action_buttons.short_description = "عملیات"


class ActionButtonsMixin:
    """Mixin برای اضافه کردن ستون عملیات (ویرایش + حذف) به ادمین"""

    def admin_actions(self, obj):
        return admin_action_buttons(obj)

    admin_actions.short_description = "عملیات"


@admin.register(CompanyCatalog)
class CompanyCatalogAdmin(ActionButtonsMixin, admin.ModelAdmin):
    actions = None  # ❌ حذف bulk actions

    # ================================
    # List View
    # ================================
    list_display = (
        "title_fa",
        "updated_at_jalali_display",
        "updated_at_gregorian_display",
        "admin_actions",
    )

    ordering = ("-updated_at",)
    search_fields = ("title_fa",)

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
            "fields": ("title_fa", "title_en", "description_fa", "description_en", "pdf_file"),
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

    updated_at_jalali_display.short_description_fa = "آخرین بروزرسانی (شمسی)"

    def updated_at_gregorian_display(self, obj):
        return obj.updated_at_gregorian

    updated_at_gregorian_display.short_description_fa = "آخرین بروزرسانی (میلادی)"