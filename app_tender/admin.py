# app_tender/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import TenderCategory, TenderTag, Tender, TenderImage


# -------------------------------------------------------
#   GLOBAL ACTION BUTTONS (EDIT + DELETE)
# -------------------------------------------------------
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
# ⚠️ short_description روی تابع ماژول‌سطح کار نمی‌کنه — فقط روی متد کلاس


class ActionButtonsMixin:
    """Mixin برای اضافه کردن ستون عملیات (ویرایش + حذف) به ادمین"""

    def admin_actions(self, obj):
        return admin_action_buttons(obj)

    admin_actions.short_description = "عملیات"


# -------------------------------------------------------
#   INLINE — Tender Images
# -------------------------------------------------------
class TenderImageInline(admin.TabularInline):
    model = TenderImage
    extra = 1
    fields = ("show_image", "image", "caption", "order")
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
class TenderCategoryAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
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
    readonly_fields = ("slug", "slug_en", "created_at_fa", "updated_at_fa")

    # ✅ order + زمان ایجاد
    fieldsets = (
        (None, {
            "fields": ("title_fa", "title_en", "slug", "slug_en", "order"),
        }),
        ("⏱️ زمان", {
            "fields": ("created_at_fa", "updated_at_fa"),
            "classes": ("collapse",),
        }),
    )

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# -------------------------------------------------------
#   TAG ADMIN
# -------------------------------------------------------
@admin.register(TenderTag)
class TenderTagAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
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
    readonly_fields = ("slug", "slug_en", "created_at_fa", "updated_at_fa")

    # ✅ order + زمان ایجاد
    fieldsets = (
        (None, {
            "fields": ("title_fa", "title_en", "slug", "slug_en", "order"),
        }),
        ("⏱️ زمان", {
            "fields": ("created_at_fa", "updated_at_fa"),
            "classes": ("collapse",),
        }),
    )

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# -------------------------------------------------------
#   TENDER ADMIN (Main)
# -------------------------------------------------------
@admin.register(Tender)
class TenderAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    ✅ SortableAdminMixin اضافه شد تا order قابل drag & drop باشه
    """
    actions = None
    inlines = [TenderImageInline]

    list_display = (
        "order",
        "poster_icon",
        "title_icon",
        "status_icon",
        "category_icon",
        "tag_icon",
        "start_date_fa",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "tender_number", "slug", "slug_en")
    list_filter = ("status", "category")
    readonly_fields = ("poster_preview", "slug", "slug_en")
    ordering = ("order",)

    fieldsets = (
        ("📌 وضعیت", {
            "fields": ("status",),
        }),
        ("🖼️ تصویر", {
            "fields": ("poster", "poster_preview"),
        }),
        ("📄 فارسی", {
            "fields": ("title_fa", "description_fa", "slug"),
        }),
        ("📄 انگلیسی", {
            "fields": ("title_en", "description_en", "slug_en"),
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
        ("🔢 ترتیب", {
            "fields": ("order",),
        }),
        ("🗓️ تاریخ‌ها", {
            "fields": (
                "start_date_fa", "end_date_fa",
                "start_date_en", "end_date_en",
            ),
        }),
    )

    # ---------- ICONS ----------
    def poster_icon(self, obj):
        if obj.poster:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; "
                "box-shadow:0 0 4px #aaa;'>",
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

    poster_preview.short_description = "پیش‌نمایش پوستر"

    def title_icon(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def status_icon(self, obj):
        colors = {
            "ongoing": "#198754",
            "extended": "#fd7e14",
            "finished": "#dc3545",
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
        # ✅ tags.exists() جای if not tags
        if not tags.exists():
            return "—"
        return " ، ".join([t.title_fa for t in tags])

    tag_icon.short_description = "برچسب‌ها"