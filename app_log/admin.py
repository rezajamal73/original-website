from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_per_page = 50

    list_display = (
        "created_at_jalali",
        "created_at",
        "action",
        "app_name",
        "model_name",
        "object_id",
        "object_name",
        "user",
        "ip_address",
    )

    list_filter = (
        "action",
        "app_name",
        "model_name",
        "created_at",
    )

    search_fields = (
        "object_name",
        "app_name",
        "model_name",
        "object_id",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "action",
        "app_name",
        "model_name",
        "object_id",
        "object_name",
        "user",
        "ip_address",
        "old_json",
        "new_json",
    )

    actions = None

    fieldsets = (
        (
            "📜 اطلاعات لاگ",
            {
                "fields": (
                    "created_at",
                    "action",
                    "app_name",
                    "model_name",
                    "object_id",
                    "object_name",
                    "user",
                    "ip_address",
                )
            },
        ),
        (
            "📥 اطلاعات قبلی",
            {
                "fields": (
                    "old_json",
                )
            },
        ),
        (
            "📤 اطلاعات جدید",
            {
                "fields": (
                    "new_json",
                )
            },
        ),
    )

    def old_json(self, obj):
        return mark_safe(
            f"<pre style='white-space:pre-wrap'>{obj.old_data}</pre>"
        )

    old_json.short_description = "اطلاعات قبلی"

    def new_json(self, obj):
        return mark_safe(
            f"<pre style='white-space:pre-wrap'>{obj.new_data}</pre>"
        )

    new_json.short_description = "اطلاعات جدید"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False