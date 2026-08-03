from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import SEOSetting


@admin.register(SEOSetting)
class SEOSettingAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "content_type_badge",
        "page_key",
        "app_label",
        "model_name",
        "object_id",
        "status_badge",
        "updated_at",
        "delete_action",
    )

    list_display_links = ("title",)

    list_filter = (
        "content_type",
        "is_active",
        "app_label",
    )

    search_fields = (
        "title",
        "description",
        "keywords",
        "page_key",
        "app_label",
        "model_name",
        "object_id",
    )

    ordering = (
        "content_type",
        "title",
    )

    list_per_page = 50

    readonly_fields = (
        "created_at",
        "updated_at",
        "og_preview",
    )

    fieldsets = (
        (
            "📌 اتصال و مشخصات محتوا",
            {
                "description": "مشخص کنید این تنظیمات SEO برای کدام صفحه، محصول یا محتوای سایت است.",
                "fields": (
                    "content_type",
                    "page_key",
                    "app_label",
                    "model_name",
                    "object_id",
                    "url",
                    "is_active",
                ),
            },
        ),
        (
            "🔍 تنظیمات اصلی موتور جستجو (Meta SEO)",
            {
                "description": "اطلاعاتی که موتورهای جستجو مانند گوگل برای نمایش صفحه استفاده می‌کنند.",
                "fields": (
                    "title",
                    "description",
                    "keywords",
                    "canonical",
                    "robots",
                ),
            },
        ),
        (
            "🌐 شبکه‌های اجتماعی (Open Graph)",
            {
                "description": "اطلاعات نمایش صفحه هنگام اشتراک‌گذاری در شبکه‌های اجتماعی.",
                "fields": (
                    "og_title",
                    "og_description",
                    "og_type",
                    "og_image",
                    "og_preview",
                ),
            },
        ),
        (
            "🧩 اطلاعات ساختاریافته گوگل (Schema JSON-LD)",
            {
                "fields": (
                    "schema_json",
                ),
            },
        ),
        (
            "🕒 اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="نوع محتوا")
    def content_type_badge(self, obj):
        return obj.get_content_type_display()

    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color:#198754;font-weight:bold;">● فعال</span>'
            )

        return format_html(
            '<span style="color:#dc3545;font-weight:bold;">● غیرفعال</span>'
        )

    @admin.display(description="پیش‌نمایش تصویر OG")
    def og_preview(self, obj):
        if obj.og_image:
            return format_html(
                '<img src="{}" style="max-width:350px;border-radius:8px;">',
                obj.og_image.url,
            )

        return "تصویری انتخاب نشده"

    @admin.display(description="حذف")
    def delete_action(self, obj):
        url = reverse(
            "admin:app_seo_seosetting_delete",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}" style="color:#dc3545;font-weight:bold;">🗑 حذف</a>',
            url,
        )