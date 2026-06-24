# app_media/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin

from .models import Media, MediaImage, MediaVideo


def admin_delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
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
        url,
    )
admin_delete_button.short_description = "حذف"


class MediaImageInline(admin.TabularInline):
    model = MediaImage
    extra = 1
    readonly_fields = ("show_image",)
    fields = ("show_image", "image", "order")

    def show_image(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='80' "
                "style='border-radius:8px; box-shadow:0 0 6px #aaa;'>",
                obj.image.url,
            )
        return "—"
    show_image.short_description = "پیش‌نمایش"


class MediaVideoInline(admin.TabularInline):
    model = MediaVideo
    extra = 1
    readonly_fields = ("show_video",)
    fields = ("show_video", "video", "order")

    def show_video(self, obj):
        if obj.video:
            return format_html(
                "<video width='120' height='80' controls "
                "style='border-radius:8px; box-shadow:0 0 6px #aaa;'>"
                "<source src='{}'></video>",
                obj.video.url,
            )
        return "—"
    show_video.short_description = "پیش‌نمایش"


@admin.register(Media)
class MediaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "order",
        "image_icon",
        "title_icon",
        "status_icon",
        "special_icon",
        admin_delete_button,
    )

    ordering = ("order",)
    actions = None

    search_fields = ("title_fa", "title_en", "summary_fa", "summary_en")
    list_filter = ("status", "is_special")

    readonly_fields = ("slug", "show_image_in_field")

    inlines = [MediaImageInline, MediaVideoInline]

    fieldsets = (
        ("📌 وضعیت", {"fields": ("status", "is_special")}),
        ("🖼️ تصویر", {"fields": ("image", "show_image_in_field")}),
        ("📝 فارسی", {"fields": ("title_fa", "summary_fa")}),
        ("📝 انگلیسی", {"fields": ("title_en", "summary_en", "slug")}),
    )

    def image_icon(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='45' height='45' "
                "style='border-radius:6px; object-fit:cover; "
                "box-shadow:0 0 4px #aaa;'>",
                obj.image.url,
            )
        return "🖼️"
    image_icon.short_description = "عکس"

    def show_image_in_field(self, obj):
        if obj.image:
            return format_html(
                "<img src='{}' width='180' "
                "style='border-radius:10px; box-shadow:0 0 10px #aaa;'>",
                obj.image.url,
            )
        return "تصویری آپلود نشده است"
    show_image_in_field.short_description = "پیش‌نمایش"

    def title_icon(self, obj):
        return format_html(
            "<b style='color:#1A73E8'>{}</b>",
            obj.title_fa,
        )
    title_icon.short_description = "عنوان"

    def status_icon(self, obj):
        if obj.status == "published":
            return format_html(
                "<b style='color:green;'>{}</b>",
                "منتشر شده",
            )
        return format_html(
            "<b style='color:red;'>{}</b>",
            "پیش‌نویس",
        )
    status_icon.short_description = "وضعیت"

    def special_icon(self, obj):
        return "⭐" if obj.is_special else "—"
    special_icon.short_description = "نمایش در صفحه اصلی"