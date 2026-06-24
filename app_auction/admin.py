from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import AuctionCategory, AuctionTag, Auction, AuctionImage

"""
admin.py — مدیریت ادمین برای اپلیکیشن مزایده‌ها (Auction).
توضیحات کلی:
- دکمهٔ حذف کلی (admin_delete_button) برای همه‌ی مدل‌ها ارائه شده.
- Inline برای تصاویر مزایده (AuctionImageInline) با پیش‌نمایش (preview).
- Admin های مرتب‌شونده (SortableAdminMixin) برای دسته‌بندی و تگ‌ها.
- AuctionAdmin شامل پیش‌نمایش پوستر، آیکون‌ها و دکمهٔ حذف است.

تضمین‌ها:
- از format_html برای درج HTML امن استفاده شده است.
- فیلدهای قابل‌ویرایش/readonly مشخص شده‌اند.
"""

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
#   INLINE: Auction Images
# ---------------------------------------------------
class AuctionImageInline(admin.TabularInline):
    """
    Inline برای مدیریت تصاویر مزایده.
    فیلدها: پیش‌نمایش (readonly), image, order
    """
    model = AuctionImage
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
#   CATEGORY ADMIN (Sortable)
# ---------------------------------------------------
# ---------------------------------------------------
#   AUCTION CATEGORY ADMIN (with icon)
# ---------------------------------------------------
@admin.register(AuctionCategory)
class AuctionCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت دسته‌بندی‌های مزایده (AuctionCategory).
    امکانات:
    - نمایش آیکون پوشه کنار عنوان
    - قابل مرتب‌سازی توسط adminsortable2
    - دکمه حذف یکپارچه
    """
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "created_at_fa",
        "delete_button",
    )

    search_fields = ("title_fa", "title_en", "slug")
    ordering = ("order",)
    list_display_links = ("title_icon",)
    readonly_fields = ("slug",)

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug")}),
    )

    # ---------- ICON TITLE ----------
    def title_icon(self, obj):
        """نمایش آیکون پوشه کنار عنوان فارسی"""
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"

# ---------------------------------------------------
#   AUCTION TAG ADMIN (with icon)
# ---------------------------------------------------
@admin.register(AuctionTag)
class AuctionTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت تگ‌های مزایده (AuctionTag).
    امکانات:
    - نمایش آیکون تگ کنار عنوان
    - قابل مرتب‌سازی
    - دکمه حذف یکپارچه
    """
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "created_at_fa",
        "delete_button",
    )

    search_fields = ("title_fa", "title_en", "slug")
    ordering = ("order",)
    list_display_links = ("title_icon",)
    readonly_fields = ("slug",)

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug")}),
    )

    # ---------- ICON TITLE ----------
    def title_icon(self, obj):
        """نمایش آیکون تگ کنار عنوان فارسی"""
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"

# ---------------------------------------------------
#   AUCTION ADMIN (Pro)
# ---------------------------------------------------
@admin.register(Auction)
class AuctionAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    مدیریت مزایده‌ها.
    امکانات:
    - پیش‌نمایش پوستر و آیکن کوچک در لیست
    - لینک‌های جستجو و فیلترها
    - inline تصاویر مرتبط
    - دکمهٔ حذف برای هر سطر
    """
    actions = None
    inlines = [AuctionImageInline]
    readonly_fields = ("poster_preview", "slug")
    list_display = (
        "order",
        "poster_icon",
        "title_fa_display",
        "status_display",
        "category_display",
        "start_date_fa",
        "delete_button",
    )
    search_fields = ("title_fa", "title_en", "call_number", "slug")
    list_filter = ("status", "category", "start_date_fa")
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

    # ---------- ICONS & PREVIEWS ----------
    def poster_icon(self, obj):
        """
        آیکون کوچکِ پوستر (برای نمایش در لیست).
        در صورت نبود تصویر، ایموجی نمایش می‌دهد.
        """
        if obj and getattr(obj, "poster", None):
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.poster.url,
            )
        return "🖼️"

    poster_icon.short_description = "عکس"

    def poster_preview(self, obj):
        """پیش‌نمایش بزرگ‌تر پوستر در فرم تغییر/ایجاد."""
        if obj and getattr(obj, "poster", None):
            return format_html(
                "<img src='{}' width='180' style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.poster.url,
            )
        return "—"

    poster_preview.short_description = "پیش‌نمایش پوستر"

    def title_fa_display(self, obj):
        """نمایش عنوان فارسی با استایل مشخص."""
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa or "—")

    title_fa_display.short_description = "عنوان"

    # ---------------------------------------------------
    #   STATUS DISPLAY (Human readable + colored)
    # ---------------------------------------------------
    def status_display(self, obj):
        """
        وضعیت را به صورت متن فارسی و رنگی نشان می‌دهد.
        انتظارداریم فیلد status مقادیری مثل: 'ongoing', 'extended', 'finished' داشته باشد.
        """
        colors = {
            "ongoing": "#198754",   # سبز Bootstrap-like
            "extended": "#fd7e14",  # نارنجی
            "finished": "#dc3545",  # قرمز
        }
        labels = {
            "ongoing": "در حال برگزاری",
            "extended": "تمدید شده",
            "finished": "پایان یافته",
        }
        status = getattr(obj, "status", None)
        color = colors.get(status, "#6c757d")  # خاکستری پیش‌فرض
        label = labels.get(status, str(status) if status else "نامشخص")
        return format_html("<b style='color:{}'>{}</b>", color, label)

    status_display.short_description = "وضعیت"

    def category_display(self, obj):
        """نمایش نام دسته‌بندی (فارسی) یا خط تیره در صورت نبود."""
        return obj.category.title_fa if getattr(obj, "category", None) else "—"

    category_display.short_description = "دسته‌بندی"

    def delete_button(self, obj):
        """دکمهٔ حذف در انتهای سطر لیست."""
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"
