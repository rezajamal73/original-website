# app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import (
    InquiryCategory,
    InquiryTag,
    PurchaseInquiry,
    PurchaseInquiryImage,
)

# ------------------------------------------------
#   GLOBAL DELETE BUTTON
# ------------------------------------------------
def admin_delete_button(obj):
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
#   INLINE: GALLERY IMAGES
# ---------------------------------------------------
class PurchaseInquiryImageInline(admin.TabularInline):
    model = PurchaseInquiryImage
    extra = 1
    fields = ("preview", "image", "caption", "order")
    readonly_fields = ("preview",)
    ordering = ("order",)

    def preview(self, obj):
        if obj and getattr(obj, "image", None):
            return format_html(
                "<img src='{}' width='70' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 5px #bbb;'>",
                obj.image.url,
            )
        return "—"

    preview.short_description = "پیش‌نمایش"


# ---------------------------------------------------
#   CATEGORY ADMIN
# ---------------------------------------------------
@admin.register(InquiryCategory)
class InquiryCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "created_at_fa",
        "delete_button",
    )
    ordering = ("order",)
    search_fields = ("title_fa", "title_en", "slug")
    readonly_fields = ("slug",)

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"


# ---------------------------------------------------
#   TAG ADMIN
# ---------------------------------------------------
@admin.register(InquiryTag)
class InquiryTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    actions = None

    list_display = (
        "order",
        "title_icon",
        "slug",
        "created_at_fa",
        "delete_button",
    )
    ordering = ("order",)
    search_fields = ("title_fa", "title_en", "slug")
    readonly_fields = ("slug",)

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"


# ---------------------------------------------------
#   PURCHASE INQUIRY ADMIN (FULL)
# ---------------------------------------------------
@admin.register(PurchaseInquiry)
class PurchaseInquiryAdmin(SortableAdminMixin, admin.ModelAdmin):
    actions = None
    inlines = [PurchaseInquiryImageInline]

    readonly_fields = ("slug", "cover_preview")

    list_display = (
        "order",
        "cover_icon",
        "title_fa_display",
        "status_display",
        "category_display",
        "start_date_fa",
        "delete_button",
    )

    ordering = ("order",)
    search_fields = (
        "title_fa",
        "title_en",
        "description_fa",
        "description_en",
        "inquiry_number",
        "slug",
    )
    list_filter = ("status", "category", "start_date_fa")

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status",)}),
        ("🖼️ تصویر", {"fields": ("cover_image", "cover_preview")}),
        ("📝 فارسی", {"fields": ("title_fa", "description_fa")}),
        ("📝 انگلیسی", {"fields": ("title_en", "description_en", "slug")}),
        ("📣 استعلام", {"fields": ("inquiry_number", "estimated_amount")}),
        ("📎 پیوست", {"fields": ("attachment",)}),
        ("📂 دسته‌بندی", {"fields": ("category", "tags")}),
        (
            "🗓️ تاریخ‌ها",
            {
                "fields": (
                    "start_date_fa",
                    "end_date_fa",
                    "start_date_en",
                    "end_date_en",
                )
            },
        ),
    )

    # ---------- IMAGE ICON (LIST) ----------
    def cover_icon(self, obj):
        if obj and getattr(obj, "cover_image", None):
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.cover_image.url,
            )
        return "🖼️"

    cover_icon.short_description = "عکس"

    # ---------- IMAGE PREVIEW (FORM) ----------
    def cover_preview(self, obj):
        if obj and getattr(obj, "cover_image", None):
            return format_html(
                "<img src='{}' width='180' "
                "style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.cover_image.url,
            )
        return "—"

    cover_preview.short_description = "پیش‌نمایش تصویر"

    # ---------- TEXT HELPERS ----------
    def title_fa_display(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa)

    title_fa_display.short_description = "عنوان"

    def status_display(self, obj):
        colors = {
            "open": "#198754",
            "extended": "#fd7e14",
            "closed": "#dc3545",
        }
        labels = {
            "open": "باز",
            "extended": "تمدید شده",
            "closed": "بسته شده",
        }
        return format_html(
            "<b style='color:{}'>{}</b>",
            colors.get(obj.status, "#6c757d"),
            labels.get(obj.status, obj.status),
        )

    status_display.short_description = "وضعیت"

    def category_display(self, obj):
        return obj.category.title_fa if obj.category else "—"

    category_display.short_description = "دسته‌بندی"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"
