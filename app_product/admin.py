# admin.py
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html

from adminsortable2.admin import SortableAdminMixin
from django.utils.safestring import mark_safe

from .models import (
    Product,
    ProductImage,
    ProductCategory,
    ProductCategory2,
    ProductTag,
    ProductScan,
)


# ============================================================
# GENERIC UTILITIES
# ============================================================
def delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        """
        <a href="{}" style="
            background:#dc3545;
            color:#fff;
            padding:6px 10px;
            border-radius:8px;
            text-decoration:none;
            font-weight:600;
            box-shadow:0 2px 6px rgba(0,0,0,.2);
        ">🗑</a>
        """,
        url,
    )


# ============================================================
# CATEGORY ADMIN
# ============================================================
@admin.register(ProductCategory)
class ProductCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    sortable = "priority"
    ordering = ("priority",)
    actions = None

    list_display = ("priority", "title_display", "slug", "delete_col")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("slug",)

    def title_display(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_display.short_description = "عنوان"

    def delete_col(self, obj):
        return delete_button(obj)

    delete_col.short_description = ""


# ============================================================
# CATEGORY 2 ADMIN
# ============================================================
@admin.register(ProductCategory2)
class ProductCategory2Admin(SortableAdminMixin, admin.ModelAdmin):
    sortable = "priority"
    ordering = ("priority",)
    actions = None

    list_display = ("priority", "title_display", "slug", "delete_col")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("slug",)

    def title_display(self, obj):
        return format_html("📂 <b>{}</b>", obj.title_fa)

    title_display.short_description = "عنوان"

    def delete_col(self, obj):
        return delete_button(obj)

    delete_col.short_description = ""


# ============================================================
# TAG ADMIN
# ============================================================
@admin.register(ProductTag)
class ProductTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    sortable = "priority"
    ordering = ("priority",)
    actions = None

    list_display = ("priority", "title_display", "slug", "delete_col")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("slug",)

    def title_display(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_display.short_description = "عنوان"

    def delete_col(self, obj):
        return delete_button(obj)

    delete_col.short_description = ""


# ============================================================
# PRODUCT IMAGE INLINE
# ============================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10
    fields = ("order", "preview", "image")
    readonly_fields = ("preview",)
    ordering = ("order",)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" width="70" style="border-radius:8px;box-shadow:0 0 6px #aaa;">',
                obj.image.url,
            )
        return "—"

    preview.short_description = "پیش‌نمایش"


# ============================================================
# PRODUCT SCAN INLINE
# ============================================================
class ProductScanInline(admin.TabularInline):
    model = ProductScan
    extra = 0
    can_delete = False
    readonly_fields = ("scanned_at", "ip_address", "user_agent")
    ordering = ("-scanned_at",)

    def has_add_permission(self, request, obj=None):
        return False


# ============================================================
# PRODUCT ADMIN
# ============================================================
@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    sortable = "priority"
    ordering = ("priority",)
    actions = None

    autocomplete_fields = ("category", "tags")
    inlines = (ProductImageInline, ProductScanInline)

    search_fields = (
        "title_fa",
        "title_en",
        "generic_name_fa",
        "generic_name_en",
        "sku",
    )

    list_filter = ("status", "category")

    list_display = (
        "priority",
        "image_col",
        "title_col",
        "category_col",
        "status_col",
        "sku",
        "created_col",
        "delete_col",
    )

    readonly_fields = (
        "slug",
        "created_col",
        "updated_col",
        "main_image_preview",
        "qr_preview",
        "qr_data",
    )

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 4})}
    }

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status", "special")}),
        ("🆔 هویت محصول", {"fields": ( "sku","title_fa", "title_en", "generic_name_fa", "generic_name_en","summary_fa",)}),
        ("🖼️ تصویر", {"fields": ("main_image", "main_image_preview")}),
        ("📂️ دسته‌بندی", {"fields": ("category","category2", "tags")}),

        ("📄 فارسی", {
            "fields": (
                "composition_fa",
                "indications_fa",
                "contra_fa",
                "warnings_fa",
                "pregnancy_use_fa",
                "instructions_fa",
                "description_fa",
            ),
        }),

        ("📄 انگلیسی", {
            "fields": (
                "composition_en",
                "indications_en",
                "contra_en",
                "warnings_en",
                "pregnancy_use_en",
                "instructions_en",
                "description_en",
            ),
            "classes": ("collapse",),
        }),

        ("QR Code 🔐", {
            "fields": ("qr_data", "qr_preview"),
            "classes": ("collapse",),
        }),
    )

    # -------------------------
    # DISPLAY HELPERS
    # -------------------------
    def image_col(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="55" style="border-radius:6px;box-shadow:0 0 4px #aaa;">',
                obj.main_image.url,
            )
        return "🖼️"

    image_col.short_description = "تصویر"

    def title_col(self, obj):
        return format_html("<b style='color:#0d6efd'>{}</b>", obj.title_fa)

    title_col.short_description = "عنوان"

    def category_col(self, obj):
        return obj.category.title_fa if obj.category else "—"

    category_col.short_description = "دسته"

    def status_col(self, obj):
        return (
            mark_safe("<b style='color:green'>✅ منتشر</b>")
            if obj.status == "published"
            else mark_safe("<b style='color:#dc3545'>⛔ پیش‌نویس</b>")
        )

    status_col.short_description = "وضعیت"

    def created_col(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    created_col.short_description = "ایجاد"

    def updated_col(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    updated_col.short_description = "ویرایش"

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:10px;box-shadow:0 0 6px #aaa;">',
                obj.main_image.url,
            )
        return "—"

    main_image_preview.short_description = "پیش‌نمایش تصویر"

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="140" style="border:1px solid #ddd;padding:6px;border-radius:8px;">',
                obj.qr_code.url,
            )
        return "QR ساخته نشده"

    qr_preview.short_description = "QR Code"

    def delete_col(self, obj):
        return delete_button(obj)

    delete_col.short_description = ""
