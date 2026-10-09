from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin

from .models import Resume, ResumeProvince


# =====================================================
# GLOBAL ACTION BUTTONS (EDIT + DELETE)
# =====================================================
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


# =====================================================
# RESUME PROVINCE ADMIN
# =====================================================
@admin.register(ResumeProvince)
class ResumeProvinceAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_order",
        "province_name_fa",
        "province_name_en",
        "admin_actions",
    )

    list_display_links = (
        "province_name_fa",
    )

    search_fields = (
        "province_name_fa",
        "province_name_en",
    )

    ordering = ("display_order",)

    actions = None

    fieldsets = (
        (
            "📍 اطلاعات استان / شهر",
            {
                "fields": (
                    "province_name_fa",
                    "province_name_en",
                    "display_order",
                )
            },
        ),
    )


# =====================================================
# RESUME ADMIN
# =====================================================
@admin.register(Resume)
class ResumeAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_order",
        "svg_preview",
        "project_name_fa",
        "project_name_en",
        "province_name",
        "created_at",
        "admin_actions",
    )

    list_display_links = (
        "project_name_fa",
    )

    search_fields = (
        "project_name_fa",
        "project_name_en",
        "province__province_name_fa",
        "province__province_name_en",
    )

    list_filter = (
        "province",
    )

    ordering = (
        "display_order",
    )

    readonly_fields = (
        "svg_preview_large",
        "created_at",
    )

    actions = None

    fieldsets = (
        (
            "📂 اطلاعات پروژه",
            {
                "fields": (
                    "project_name_fa",
                    "project_name_en",
                    "province",
                )
            },
        ),
        ("🎨 فایل گرافیکی (SVG)", {
            "fields": (
                "svg_file",
                "svg_preview_large",
            )
        }),
        (
            "🔢 تنظیمات نمایش",
            {
                "fields": (
                    "display_order",
                )
            },
        ),
        (
            "🕒 اطلاعات",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    def province_name(self, obj):
        return obj.province.province_name_fa

    province_name.short_description = "استان / شهر"

    def svg_preview(self, obj):
        if obj.svg_file:
            return format_html(
                "<img src='{}' width='40' height='40' "
                "style='border:1px solid #ddd;padding:3px;border-radius:6px;'>",
                obj.svg_file.url,
            )
        return "—"

    svg_preview.short_description = "SVG"

    def svg_preview_large(self, obj):
        if obj.svg_file:
            return format_html(
                "<img src='{}' width='180' "
                "style='border:1px solid #ddd;padding:8px;border-radius:8px;'>",
                obj.svg_file.url,
            )
        return "فایلی وجود ندارد."

    svg_preview_large.short_description = "پیش‌نمایش"