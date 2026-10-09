from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import AuctionCategory, AuctionTag, Auction, AuctionImage


# ------------------------------------------------
#   GLOBAL ACTION BUTTONS (EDIT + DELETE)
# ------------------------------------------------
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
                    display:inline-block;
               ">
               ✏️ ویرایش
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
                    display:inline-block;
               ">
               🗑 حذف
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
#   INLINE: Auction Images
# ---------------------------------------------------
class AuctionImageInline(admin.TabularInline):
    model = AuctionImage
    extra = 1
    fields = ("preview", "image", "order")
    readonly_fields = ("preview",)
    ordering = ("order",)

    def preview(self, obj):
        if obj and getattr(obj, "image", None):
            return format_html(
                '<img src="{}" width="70" style="border-radius:6px; '
                'object-fit:cover; box-shadow:0 0 5px #bbb;" />',
                obj.image.url,
            )
        return "—"

    preview.short_description = "پیش‌نمایش"


# ---------------------------------------------------
#   AUCTION CATEGORY ADMIN
# ---------------------------------------------------
@admin.register(AuctionCategory)
class AuctionCategoryAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
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
    list_display_links = ("title_icon",)
    readonly_fields = ("slug", "slug_en")

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug", "slug_en", "order")}),
    )

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# ---------------------------------------------------
#   AUCTION TAG ADMIN
# ---------------------------------------------------
@admin.register(AuctionTag)
class AuctionTagAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
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
    list_display_links = ("title_icon",)
    readonly_fields = ("slug", "slug_en")

    fieldsets = (
        (None, {"fields": ("title_fa", "title_en", "slug", "slug_en", "order")}),
    )

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"


# ---------------------------------------------------
#   AUCTION ADMIN
# ---------------------------------------------------
@admin.register(Auction)
class AuctionAdmin(ActionButtonsMixin, SortableAdminMixin, admin.ModelAdmin):
    actions = None
    inlines = [AuctionImageInline]
    readonly_fields = ("poster_preview", "slug", "slug_en")

    list_display = (
        "order",
        "poster_icon",
        "title_fa_display",
        "status_display",
        "category_display",
        "start_date_fa",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "call_number", "slug", "slug_en")
    list_filter = ("status", "category", "start_date_fa")
    ordering = ("order",)

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status",)}),
        ("🖼️ تصویر", {"fields": ("poster", "poster_preview",)}),
        ("📝 فارسی", {"fields": ("title_fa", "description_fa", "slug")}),
        ("📝 انگلیسی", {"fields": ("title_en", "description_en", "slug_en")}),
        ("📣 فراخوان", {"fields": ("call_number", "estimated_amount")}),
        ("📎 پیوست", {"fields": ("upload_file",)}),
        ("📂 دسته‌بندی", {"fields": ("category", "tags")}),
        ("🗓️ تاریخ‌ها", {"fields": ("start_date_fa", "end_date_fa", "start_date_en", "end_date_en")}),
    )

    # ---------- ICONS & PREVIEWS ----------
    def poster_icon(self, obj):
        if obj and getattr(obj, "poster", None):
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.poster.url,
            )
        return "🖼️"

    poster_icon.short_description = "عکس"

    def poster_preview(self, obj):
        if obj and getattr(obj, "poster", None):
            return format_html(
                "<img src='{}' width='180' style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.poster.url,
            )
        return "—"

    poster_preview.short_description = "پیش‌نمایش پوستر"

    def title_fa_display(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa or "—")

    title_fa_display.short_description = "عنوان"

    def status_display(self, obj):
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
        status = getattr(obj, "status", None)
        color = colors.get(status, "#6c757d")
        label = labels.get(status, str(status) if status else "نامشخص")
        return format_html("<b style='color:{}'>{}</b>", color, label)

    status_display.short_description = "وضعیت"

    def category_display(self, obj):
        return obj.category.title_fa if getattr(obj, "category", None) else "—"

    category_display.short_description = "دسته‌بندی"