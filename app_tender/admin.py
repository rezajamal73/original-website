# app_tender/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import TenderCategory, TenderTag, Tender, TenderImage


# -------------------------------------------------------
#   GLOBAL DELETE BUTTON
# -------------------------------------------------------
def admin_delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk]
    )
    return format_html(
        """
        <a href="{}"
           style="
               background:#d7263d;
               color:white;
               padding:6px 10px;
               border-radius:8px;
               text-decoration:none;
               font-weight:bold;
               display:inline-flex;
               align-items:center;
               gap:5px;
               box-shadow:0 2px 5px rgba(0,0,0,0.2);
           ">
            🗑
        </a>
        """,
        url
    )


# -------------------------------------------------------
#   INLINE — Tender Images
# -------------------------------------------------------
class TenderImageInline(admin.TabularInline):
    model = TenderImage
    extra = 1
    fields = ("show_image", "image", "order")
    ordering = ("order",)
    readonly_fields = ("show_image",)

    def show_image(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='80' "
                "style='border-radius:8px; box-shadow:0 0 6px #aaa;'>",
                obj.image.url
            )
        return "—"

    show_image.short_description = "پیش‌نمایش"


# -------------------------------------------------------
#   CATEGORY ADMIN
# -------------------------------------------------------
@admin.register(TenderCategory)
class TenderCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("slug",)

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)


# -------------------------------------------------------
#   TAG ADMIN
# -------------------------------------------------------
@admin.register(TenderTag)
class TenderTagAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "title_icon", "slug", "created_at_fa", "delete_button")
    search_fields = ("title_fa", "title_en")
    readonly_fields = ("slug",)

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def delete_button(self, obj):
        return admin_delete_button(obj)


# -------------------------------------------------------
#   TENDER ADMIN (Main)
# -------------------------------------------------------
@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):

    inlines = [TenderImageInline]

    list_display = (
        "poster_icon",
        "title_icon",
        "status_icon",
        "category_icon",
        "tag_icon",     # ← اینجا کاما اضافه شد ✔️
        "start_date_fa",
        "delete_button",
    )

    search_fields = ("title_fa", "title_en", "tender_number", "slug")
    list_filter = ("status", "category")
    readonly_fields = ("poster_preview", "slug")
    ordering = ("order",)

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("status",),
            "classes": ("collapse",),
        }),
        ("🖼️ تصویر", {
            "fields": ("poster", "poster_preview"),
        }),
        ("📄 فارسی", {
            "fields": ("title_fa", "description_fa"),
        }),
        ("📄 انگلیسی", {
            "fields": ("title_en", "description_en", "slug"),
        }),
        ("📣 فراخوان", {
            "fields": ("tender_number", "estimated_amount"),
        }),
        ("📎 پیوست", {
            "fields": ("upload_file",),
        }),
        ("📂 دسته‌بندی", {
            "fields": ("category", "tags"),
        }),
        ("🗓️ تاریخ‌ها", {
            "fields": ("start_date_fa", "end_date_fa", "start_date_en", "end_date_en"),
        }),
    )

    # ---------- ICONS ----------
    def poster_icon(self, obj):
        if obj.poster:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.poster.url
            )
        return "🖼️"

    poster_icon.short_description = "عکس"

    def poster_preview(self, obj):
        if obj.poster:
            return format_html(
                "<img src='{}' width='180' "
                "style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.poster.url
            )
        return "—"

    def title_icon(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def status_icon(self, obj):
        colors = {
            "ongoing": "green",
            "extended": "orange",
            "finished": "red",
        }
        labels = {
            "ongoing": "در حال برگزاری",
            "extended": "تمدید شده",
            "finished": "پایان یافته",
        }

        return format_html(
            "<b style='color:{}; font-weight:bold'>{}</b>",
            colors.get(obj.status, "gray"),
            labels.get(obj.status, "نامشخص")
        )

    status_icon.short_description = "وضعیت"

    def category_icon(self, obj):
        return obj.category.title_fa if obj.category else "—"

    category_icon.short_description = "دسته‌بندی"

    # ---------- TAG ICON ----------
    def tag_icon(self, obj):
        tags = obj.tags.all()
        if not tags:
            return "—"
        return " ، ".join([t.title_fa for t in tags])

    tag_icon.short_description = "برچسب‌ها"

    def delete_button(self, obj):
        return admin_delete_button(obj)

    delete_button.short_description = "عملیات"
