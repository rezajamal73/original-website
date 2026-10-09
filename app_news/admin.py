# app_news/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from app_news.models import (
    News,
    NewsCategory,
    NewsTag,
    NewsImage,
    NewsVideo,
)


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


admin_action_buttons.short_description = "عملیات"


class ActionButtonsMixin:
    """Mixin برای اضافه کردن ستون عملیات (ویرایش + حذف) به ادمین"""

    def admin_actions(self, obj):
        return admin_action_buttons(obj)

    admin_actions.short_description = "عملیات"


# -------------------------------------------------------
#   INLINE: IMAGE
# -------------------------------------------------------
class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    readonly_fields = ("show_image",)
    fields = ("show_image", "image", "order")

    def show_image(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='80' style='border-radius:8px; box-shadow:0 0 6px #aaa;'>",
                obj.image.url,
            )
        return "—"

    show_image.short_description = "پیش‌نمایش"


# -------------------------------------------------------
#   INLINE: VIDEO
# -------------------------------------------------------
class NewsVideoInline(admin.TabularInline):
    model = NewsVideo
    extra = 1
    readonly_fields = ("show_video",)
    fields = ("show_video", "video", "order")

    def show_video(self, obj):
        if obj.video:
            return format_html(
                """
                <video width='120' height='80' controls
                    style='border-radius:8px; box-shadow:0 0 6px #aaa;'>
                    <source src='{}' type='video/mp4'>
                </video>
                """,
                obj.video.url,
            )
        return "—"

    show_video.short_description = "پیش‌نمایش"


# =======================================================
#   CATEGORY ADMIN
# =======================================================
@admin.register(NewsCategory)
class NewsCategoryAdmin(ActionButtonsMixin, admin.ModelAdmin):
    actions = None

    list_display = (
        "title_icon",
        "slug",
        "slug_en",
        "created_icon",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "slug", "slug_en")
    ordering = ("-id",)

    readonly_fields = ("slug", "slug_en", "created_at_fa", "created_at_en")

    fieldsets = (
        ("📁 دسته‌بندی", {
            "fields": ("title_fa", "title_en", "slug", "slug_en", "order"),
        }),
        ("⏱️ زمان ایجاد", {
            "fields": ("created_at_fa", "created_at_en"),
            "classes": ("collapse",),
        }),
    )

    def title_icon(self, obj):
        return format_html("📁 <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def created_icon(self, obj):
        return format_html("⏱️ {}", obj.created_at_fa.strftime("%Y-%m-%d %H:%M:%S"))

    created_icon.short_description = "ایجاد"


# =======================================================
#   TAG ADMIN
# =======================================================
@admin.register(NewsTag)
class NewsTagAdmin(ActionButtonsMixin, admin.ModelAdmin):
    actions = None

    list_display = (
        "title_icon",
        "slug",
        "slug_en",
        "created_icon",
        "admin_actions",
    )

    search_fields = ("title_fa", "title_en", "slug", "slug_en")
    ordering = ("-created_at_fa",)

    readonly_fields = ("slug", "slug_en", "created_at_fa", "created_at_en")

    fieldsets = (
        ("🏷️ برچسب", {
            "fields": ("title_fa", "title_en", "slug", "slug_en"),
        }),
        ("⏱️ زمان ایجاد", {
            "fields": ("created_at_fa", "created_at_en"),
            "classes": ("collapse",),
        }),
    )

    def title_icon(self, obj):
        return format_html("🏷️ <b>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def created_icon(self, obj):
        return format_html("⏱️ {}", obj.created_at_fa.strftime("%Y-%m-%d %H:%M:%S"))

    created_icon.short_description = "ایجاد"


# =======================================================
#   NEWS ADMIN
# =======================================================
@admin.register(News)
class NewsAdmin(ActionButtonsMixin, admin.ModelAdmin):
    actions = None
    inlines = [NewsImageInline, NewsVideoInline]

    list_display = (
        "image_icon",
        "title_icon",
        "status_icon",
        "category_icon",
        "tag_icon",
        "date_icon",
        "admin_actions",
    )

    ordering = ("-publish_date_fa", "-id")
    list_filter = ("status", "category")

    search_fields = (
        "title_fa",
        "title_en",
        "summary_fa",
        "summary_en",
        "slug",
        "slug_en",
    )

    readonly_fields = ("slug", "slug_en", "show_image_in_field")

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status", "is_special")}),
        ("🖼️ تصویر", {"fields": ("image", "show_image_in_field")}),
        ("📝 فارسی", {
            "fields": ("title_fa", "summary_fa", "content_fa", "slug"),
        }),
        ("📝 انگلیسی", {
            "fields": ("title_en", "summary_en", "content_en", "slug_en"),
        }),
        ("📂 دسته‌بندی", {"fields": ("category", "tags")}),
        ("📰 اطلاعات اضافی", {
            "fields": ("source", "location", "views", "order"),
            "classes": ("collapse",),
        }),
        ("🗓️ تاریخ‌ها", {
            "fields": ("publish_date_fa", "publish_date_en"),
        }),
    )

    # ------------------ ICONS ------------------
    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; box-shadow:0 0 4px #aaa;'>",
                obj.image.url,
            )
        return "🖼️"

    image_icon.short_description = "عکس"

    def show_image_in_field(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='180' style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.image.url,
            )
        return "تصویری آپلود نشده است"

    show_image_in_field.short_description = "پیش‌نمایش تصویر"

    def title_icon(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.title_fa)

    title_icon.short_description = "عنوان"

    def status_icon(self, obj):
        if obj.status == "published":
            return mark_safe("<b style='color:green'>منتشر شده</b>")
        return mark_safe("<b style='color:red'>پیش‌نویس</b>")

    status_icon.short_description = "وضعیت"

    def category_icon(self, obj):
        return obj.category.title_fa if obj.category else "—"

    category_icon.short_description = "دسته‌بندی"

    def tag_icon(self, obj):
        tags = obj.tags.all()

        if not tags.exists():
            return "—"

        html = "".join([
            f"<span style='background:#E8F0FE;color:#1A73E8;padding:3px 8px;border-radius:6px;font-size:12px;'>🏷️ {t.title_fa}</span>"
            for t in tags
        ])

        return mark_safe(
            f"<div style='display:flex;flex-wrap:wrap;gap:6px;'>{html}</div>"
        )

    tag_icon.short_description = "برچسب‌ها"

    def date_icon(self, obj):
        try:
            dt = obj.publish_date_fa.strftime("%Y-%m-%d")
        except Exception:
            dt = obj.publish_date_fa
        return format_html("{}", dt)

    date_icon.short_description = "تاریخ"