from django.contrib import admin
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

    list_display_links = (
        "title",
    )

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
        "twitter_preview",
    )

    fieldsets = (

        (
            "📌 اطلاعات پایه",
            {
                "fields": (
                    "content_type",
                    "page_key",
                    "app_label",
                    "model_name",
                    "object_id",
                    "url",
                    "is_active",
                )
            }
        ),

        (
            "🔍 Meta SEO",
            {
                "fields": (
                    "title",
                    "description",
                    "keywords",
                    "canonical",
                    "robots",
                )
            }
        ),

        (
            "🌐 Open Graph",
            {
                "fields": (
                    "og_title",
                    "og_description",
                    "og_type",
                    "og_image",
                    "og_preview",
                )
            }
        ),

        (
            "🐦 Twitter",
            {
                "fields": (
                    "twitter_title",
                    "twitter_description",
                    "twitter_card",
                    "twitter_image",
                    "twitter_preview",
                )
            }
        ),

        (
            "🧩 Schema.org",
            {
                "fields": (
                    "schema_json",
                )
            }
        ),

        (
            "🕒 اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )

    @admin.display(description="نوع")
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

    @admin.display(description="Open Graph")
    def og_preview(self, obj):

        if obj.og_image:
            return format_html(
                '<img src="{}" style="max-width:350px;border-radius:8px;">',
                obj.og_image.url,
            )

        return "—"

    @admin.display(description="Twitter")
    def twitter_preview(self, obj):

        if obj.twitter_image:
            return format_html(
                '<img src="{}" style="max-width:350px;border-radius:8px;">',
                obj.twitter_image.url,
            )

        return "—"

    @admin.display(description="حذف")
    def delete_action(self, obj):
        return format_html(
            '<a href="{}delete/" style="color:#dc3545;font-weight:bold;">🗑 حذف</a>',
            obj.pk,
        )