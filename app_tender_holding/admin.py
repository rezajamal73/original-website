# app_tender_holding/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import HoldingCategory, HoldingTag, Holding, HoldingImage


# ------------------------------------------------
#   GLOBAL ACTION BUTTONS (EDIT + DELETE)
# ------------------------------------------------
def admin_action_buttons(obj):
    """
    دکمه‌های ویرایش و حذف کنار هم که به صفحات مربوطه هدایت می‌شن.
    """
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


# ---------------------------------------------------
#   INLINE: Holding Images
# ---------------------------------------------------
class HoldingImageInline(admin.TabularInline):
    """
    Inline برای مدیریت تصاویر هلدینگ.
    """
    model = HoldingImage
    extra = 1
    fields = ("preview", "image", "order")
    readonly_fields = ("preview",)
    ordering = ("order",)

    def preview(self, obj):
        """نمایش کوچک تصویر (اگر موجود باشد)."""
        if obj and getattr(obj, "image", None):
            return format_html(
                '<img src="{}" width="70" style="border-radius:6px; '
                'object-fit:cover; box-shadow:0 0 5px #bbb;" />',
                obj.image.url,
            )
        return "—"

    preview.short_description = "پیش‌نمایش"


# ---------------------------------------------------
#   HOLDING CATEGORY ADMIN
# ---------------------------------------------------
@admin.register(HoldingCategory)
class HoldingCategoryAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت دسته‌بندی‌های هلدینگ (HoldingCategory).
    """
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "slug_en",
        "created_at_fa",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "slug", "slug_en")
    ordering = ("order",)

    readonly_fields = ("slug", "slug_en")

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug", "slug_en", "order")}),
    )

    def title_icon(self, obj):
        """نمایش آیکون پوشه کنار عنوان فارسی"""
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# ---------------------------------------------------
#   HOLDING TAG ADMIN
# ---------------------------------------------------
@admin.register(HoldingTag)
class HoldingTagAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت تگ‌های هلدینگ (HoldingTag).
    """
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "slug_en",
        "created_at_fa",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "slug", "slug_en")
    ordering = ("order",)

    readonly_fields = ("slug", "slug_en")

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug", "slug_en", "order")}),
    )

    def title_icon(self, obj):
        """نمایش آیکون تگ کنار عنوان فارسی"""
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# ---------------------------------------------------
#   HOLDING ADMIN
# ---------------------------------------------------
@admin.register(Holding)
class HoldingAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت هلدینگ‌ها.
    """
    actions = None
    inlines = [HoldingImageInline]

    readonly_fields = ("slug", "slug_en", "poster_preview")

    list_display = (
        "order",
        "poster_icon",
        "title_fa_display",
        "status_display",
        "category_display",
        "start_date_fa",
        "admin_actions",
    )

    list_filter = ("status", "category")

    search_fields = ("title_fa", "title_en", "call_number", "slug", "slug_en")
    ordering = ("order",)

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status",)}),
        ("🖼️ تصویر", {"fields": ("poster", "poster_preview",)}),
        ("📝 فارسی", {"fields": ("title_fa", "description_fa", "slug")}),
        ("📝 انگلیسی", {"fields": ("title_en", "description_en", "slug_en")}),
        ("📣 فراخوان", {"fields": ("call_number", "estimated_amount")}),
        ("📎 پیوست", {"fields": ("upload_file",)}),
        ("📂 دسته‌بندی", {"fields": ("category", "tags")}),
        ("🗓️ تاریخ‌ها", {
            "fields": (
                "start_date_fa", "end_date_fa",
                "start_date_en", "end_date_en",
            )
        }),
    )

    def poster_icon(self, obj):
        """آیکون کوچکِ پوستر (برای نمایش در لیست)."""
        if obj.poster:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; "
                "box-shadow:0 0 4px #aaa;'>",
                obj.poster.url,
            )
        return "🖼️"

    poster_icon.short_description = "پوستر"

    def poster_preview(self, obj):
        """پیش‌نمایش بزرگ‌تر پوستر در فرم تغییر/ایجاد."""
        if obj.poster:
            return format_html(
                "<img src='{}' width='180' "
                "style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.poster.url,
            )
        return "—"

    poster_preview.short_description = "پیش‌نمایش پوستر"

    def title_fa_display(self, obj):
        """نمایش عنوان فارسی با استایل مشخص."""
        return format_html(
            "<b style='color:#1A73E8'>{}</b>",
            obj.title_fa or "—",
        )

    title_fa_display.short_description = "عنوان"

    def status_display(self, obj):
        """وضعیت هلدینگ را نمایش می‌دهد."""
        colors = {
            "ongoing": "#198754",
            "extended": "#fd7e14",
            "finished": "#dc3545",
        }
        return format_html(
            "<b style='color:{}'>{}</b>",
            colors.get(obj.status, "gray"),
            obj.get_status_display(),
        )

    status_display.short_description = "وضعیت"

    def category_display(self, obj):
        """نمایش نام دسته‌بندی."""
        return obj.category.title_fa if getattr(obj, "category", None) else "—"

    category_display.short_description = "دسته‌بندی"