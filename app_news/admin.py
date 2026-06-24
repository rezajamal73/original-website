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
#   GLOBAL DELETE BUTTON
# -------------------------------------------------------
def admin_delete_button(obj):
    url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=[obj.pk])
    return format_html(
        """
        <a href="{}"
            style="
                background:#d7263d;
                color:white;
                padding:6px 10px;
                border-radius:8px;
                font-weight:bold;
                text-decoration:none;
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
admin_delete_button.short_description = "حذف"


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
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("title_icon", "created_icon", admin_delete_button)
    search_fields = ("title_fa", "title_en")
    ordering = ("-id",)
    actions = None

    readonly_fields = ("slug", "created_at_fa", "created_at_en")

    fieldsets = (
        ("📁 دسته‌بندی", {"fields": ("title_fa", "title_en", "slug")}),
        ("⏱️ زمان ایجاد", {"fields": ("created_at_fa", "created_at_en")}),
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
class NewsTagAdmin(admin.ModelAdmin):
    list_display = ("title_icon", "created_icon", admin_delete_button)
    ordering = ("-created_at_fa",)
    search_fields = ("title_fa", "title_en")
    actions = None

    readonly_fields = ("slug", "created_at_fa", "created_at_en")

    fieldsets = (
        ("🏷️ برچسب", {"fields": ("title_fa", "title_en", "slug")}),
        ("⏱️ زمان ایجاد", {"fields": ("created_at_fa", "created_at_en")}),
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
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "image_icon",
        "title_icon",
        "status_icon",
        "category_icon",
        "tag_icon",
        "date_icon",
        admin_delete_button,
    )

    ordering = ("-publish_date_fa", "-id")
    actions = None
    list_filter = ("status", "category")
    search_fields = ("title_fa", "title_en", "summary_fa", "summary_en")

    readonly_fields = ("slug", "show_image_in_field")

    inlines = [NewsImageInline, NewsVideoInline]

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status",)}),
        ("🖼️ تصویر", {"fields": ("image", "show_image_in_field")}),
        ("📝 فارسی", {"fields": ("title_fa", "summary_fa", "content_fa")}),
        ("📝 انگلیسی", {"fields": ("title_en", "summary_en", "content_en", "slug")}),
        ("📂️ دسته‌بندی", {"fields": ("category", "tags")}),
        ("🗓️ تاریخ ها", {"fields": ("publish_date_fa", "publish_date_en")}),
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

    # ---------------------------------------------------
    #           TAG ICON (NEW + PROFESSIONAL)
    # ---------------------------------------------------
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


    # ---------------------------------------------------
    def date_icon(self, obj):
        try:
            dt = obj.publish_date_fa.strftime("%Y-%m-%d")
        except Exception:
            dt = obj.publish_date_fa
        return format_html("{}", dt)
    date_icon.short_description = "تاریخ"
