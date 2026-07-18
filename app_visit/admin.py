from datetime import timedelta

from django.contrib import admin, messages
from django.utils import timezone
from django.utils.formats import date_format

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "ip",
        "path",
        "formatted_date",
    )

    search_fields = ("ip", "path")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    readonly_fields = (
        "ip",
        "path",
        "user_agent",
        "created_at",
    )
    def has_add_permission(self, request):
        return False

    @admin.display(description="زمان بازدید", ordering="created_at")
    def formatted_date(self, obj):
        return date_format(obj.created_at, "Y/m/d H:i")

    def get_visit_stats(self):
        now = timezone.now()
        today = now.date()

        qs = Visit.objects

        return {
            "online": qs.filter(
                created_at__gte=now - timedelta(minutes=5)
            ).values("ip").distinct().count(),

            "today": qs.filter(
                created_at__date=today
            ).count(),

            "yesterday": qs.filter(
                created_at__date=today - timedelta(days=1)
            ).count(),

            "week": qs.filter(
                created_at__gte=now - timedelta(days=7)
            ).count(),

            "year": qs.filter(
                created_at__gte=now - timedelta(days=365)
            ).count(),

            "total": qs.count(),
        }

    def changelist_view(self, request, extra_context=None):
        stats = self.get_visit_stats()

        self.message_user(
            request,
            (
                f"🟢 آنلاین: {stats['online']} | "
                f"📅 امروز: {stats['today']} | "
                f"📆 دیروز: {stats['yesterday']} | "
                f"🗓 هفته: {stats['week']} | "
                f"📈 سال: {stats['year']} | "
                f"📦 کل: {stats['total']}"
            ),
            level=messages.INFO,
        )

        return super().changelist_view(request, extra_context)