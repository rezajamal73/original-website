from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import HoldingCategory, HoldingTag, Holding, HoldingImage


# ------------------------------------------------
#   GLOBAL DELETE BUTTON
# ------------------------------------------------
def admin_delete_button(obj):
    """
    یک دکمهٔ حذف HTML تولید می‌کند که به صفحهٔ حذف ادمین مدل هدایت می‌شود.
    پارامتر:
        obj: نمونهٔ مدل (Model instance)
    خروجی:
        Safe HTML (format_html) حاوی لینک حذف
    """
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        (
            '<a href="{}" '
            'style="background:#d7263d; color:white; padding:6px 10px; '
            'border-radius:8px; font-weight:bold; text-decoration:none; '
            'box-shadow:0 2px 5px rgba(0,0,0,0.2); display:inline-block;">'
            '🗑 حذف'
            '</a>'
        ),
        url,
    )


# ---------------------------------------------------
#   INLINE: Holding Images
# ---------------------------------------------------
class HoldingImageInline(admin.TabularInline):
    """
    Inline برای مدیریت تصاویر هلدینگ.
    فیلدها: پیش‌نمایش (readonly), image, order
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
class HoldingCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت دسته‌بندی‌های هلدینگ (HoldingCategory).
    امکانات:
    - نمایش آیکون پوشه کنار عنوان
    - قابل مرتب‌سازی توسط adminsortable2
    - دکمه حذف یکپارچه
    """
    actions = None
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en", "slug")
    ordering = ("order",)
    readonly_fields = ("slug",)

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug")}),
    )

    def title_icon(self, obj):
        """نمایش آیکون پوشه کنار عنوان فارسی"""
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"


# ---------------------------------------------------
#   HOLDING TAG ADMIN
# ---------------------------------------------------
@admin.register(HoldingTag)
class HoldingTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت تگ‌های هلدینگ (HoldingTag).
    امکانات:
    - نمایش آیکون تگ کنار عنوان
    - قابل مرتب‌سازی
    - دکمه حذف یکپارچه
    """
    actions = None
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en", "slug")
    ordering = ("order",)
    readonly_fields = ("slug",)

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug")}),
    )

    def title_icon(self, obj):
        """نمایش آیکون تگ کنار عنوان فارسی"""
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"


# ---------------------------------------------------
#   HOLDING ADMIN
# ---------------------------------------------------
@admin.register(Holding)
class HoldingAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت هلدینگ‌ها.
    امکانات:
    - پیش‌نمایش پوستر و آیکن کوچک در لیست
    - لینک‌های جستجو و فیلترها
    - inline تصاویر مرتبط
    - دکمهٔ حذف برای هر سطر
    """
    actions = None
    inlines = [HoldingImageInline]
    readonly_fields = ("slug", "poster_preview")

    list_display = (
        "order",
        "poster_icon",
        "title_fa_display",
        "status_display",
        "category_display",
        "start_date_fa",
        "delete_button",
    )

    list_filter = ("status", "category")
    search_fields = ("title_fa", "title_en", "call_number", "slug")
    ordering = ("order",)

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status",)}),
        ("🖼️ تصویر", {"fields": ("poster", "poster_preview",)}),
        ("📝 فارسی", {"fields": ("title_fa", "description_fa")}),
        ("📝 انگلیسی", {"fields": ("title_en", "description_en", "slug")}),
        ("📣 فراخوان", {"fields": ("call_number", "estimated_amount")}),
        ("📎 پیوست", {"fields": ("upload_file",)}),
        ("📂 دسته‌بندی", {"fields": ("category", "tags")}),
        ("🗓️ تاریخ‌ها", {"fields": ("start_date_fa", "end_date_fa", "start_date_en", "end_date_en")}),
    )

    def poster_icon(self, obj):
        """آیکون کوچکِ پوستر (برای نمایش در لیست)."""
        if obj.poster:
            return format_html(
                "<img src='{}' width='45' style='border-radius:6px;'>",
                obj.poster.url,
            )
        return "🖼️"

    poster_icon.short_description = "پوستر"

    def poster_preview(self, obj):
        """پیش‌نمایش بزرگ‌تر پوستر در فرم تغییر/ایجاد."""
        if obj.poster:
            return format_html(
                "<img src='{}' width='180' style='border-radius:10px;'>",
                obj.poster.url,
            )
        return "—"

    poster_preview.short_description = "پیش‌نمایش پوستر"

    def title_fa_display(self, obj):
        """نمایش عنوان فارسی با استایل مشخص."""
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa or "—")

    title_fa_display.short_description = "عنوان"

    def status_display(self, obj):
        """وضعیت هلدینگ را نمایش می‌دهد."""
        colors = {
            "ongoing": "#198754",   # سبز
            "extended": "#fd7e14",   # نارنجی
            "finished": "#dc3545",   # قرمز
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

    def delete_button(self, obj):
        """دکمهٔ حذف در انتهای سطر لیست."""
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"
