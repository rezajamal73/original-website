from datetime import timedelta
import csv

from django.contrib import admin, messages
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):

    list_display = (
        "ip",
        "page",
        "visit_count",
        "device_type_badge",
        "os_badge",
        "browser_badge",
        "device_model",
        "formatted_date",
        "last_seen_relative",
    )

    list_display_links = (
        "ip",
        "page",
    )

    search_fields = (
        "ip",
        "path",
        "user_agent",
        "referer",
        "device_model",
    )

    list_filter = (
        ("created_at", admin.DateFieldListFilter),
        "device_type",
        "os",
        "browser",
    )

    readonly_fields = (
        "ip",
        "page",
        "path",
        "user_agent",
        "referer",
        "created_at_j",
        "last_seen_j",
        "visit_count",
        "device_type",
        "os",
        "browser",
        "device_model",
        "screen_resolution",
        "language",
    )

    ordering = ("-created_at",)

    list_per_page = 850
    list_max_show_all = 850

    date_hierarchy = "created_at"

    actions = (
        "export_as_csv",
    )

    # ------------------------

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # ------------------------

    @admin.display(description="صفحه", ordering="path")
    def page(self, obj):
        return obj.page_name

    @admin.display(description="اولین بازدید", ordering="created_at")
    def formatted_date(self, obj):
        return obj.created_at_j

    @admin.display(description="آخرین فعالیت", ordering="last_seen")
    def last_seen_relative(self, obj):
        delta = timezone.now() - obj.last_seen

        if delta < timedelta(minutes=1):
            return "همین الان"

        if delta < timedelta(hours=1):
            return f"{delta.seconds // 60} دقیقه قبل"

        if delta < timedelta(days=1):
            return f"{delta.seconds // 3600} ساعت قبل"

        return obj.last_seen_j

    # ------------------------
    # نمایش دستگاه
    # ------------------------

    @admin.display(description="دستگاه", ordering="device_type")
    def device_type_badge(self, obj):
        icons = {
            "desktop": "🖥",
            "mobile": "📱",
            "tablet": "📲",
            "bot": "🤖",
            "unknown": "❓",
        }
        return f"{icons.get(obj.device_type, '❓')} {obj.get_device_type_display()}"

    @admin.display(description="سیستم‌عامل", ordering="os")
    def os_badge(self, obj):
        return obj.get_os_display()

    @admin.display(description="مرورگر", ordering="browser")
    def browser_badge(self, obj):
        return obj.get_browser_display()

    # ------------------------
    # Actions
    # ------------------------

    @admin.action(description="خروجی CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=visits.csv"

        writer = csv.writer(response)
        writer.writerow([
            "IP",
            "Page",
            "Path",
            "Visit Count",
            "Device Type",
            "OS",
            "Browser",
            "Device Model",
            "First Visit",
            "Last Activity",
        ])

        for visit in queryset:
            writer.writerow([
                visit.ip,
                visit.page_name,
                visit.path,
                visit.visit_count,
                visit.get_device_type_display(),
                visit.get_os_display(),
                visit.get_browser_display(),
                visit.device_model,
                visit.created_at_j,
                visit.last_seen_j,
            ])

        self.message_user(
            request,
            f"{queryset.count()} رکورد با موفقیت خروجی گرفته شد.",
            level=messages.SUCCESS,
        )

        return response

    # ------------------------
    # آمار
    # ------------------------

    def _sum(self, queryset):
        return queryset.count()

    def get_visit_stats(self):
        now = timezone.now()
        today = timezone.localdate()

        qs = Visit.objects.all()

        return {
            "online": qs.filter(
                last_seen__gte=now - timedelta(minutes=5)
            ).values("ip").distinct().count(),

            "today": self._sum(qs.filter(created_at__date=today)),

            "yesterday": self._sum(
                qs.filter(created_at__date=today - timedelta(days=1))
            ),

            "week": self._sum(
                qs.filter(created_at__gte=now - timedelta(days=7))
            ),

            "month": self._sum(
                qs.filter(created_at__gte=now - timedelta(days=30))
            ),

            "year": self._sum(
                qs.filter(created_at__gte=now - timedelta(days=365))
            ),

            "total": self._sum(qs),

            "unique_today": qs.filter(
                created_at__date=today
            ).values("ip").distinct().count(),

            "desktop": qs.filter(device_type="desktop").count(),
            "mobile": qs.filter(device_type="mobile").count(),
            "tablet": qs.filter(device_type="tablet").count(),
        }

    def changelist_view(self, request, extra_context=None):
        stats = self.get_visit_stats()

        self.message_user(
            request,
            (
                f"🟢 آنلاین: {stats['online']} | "
                f"👤 یکتا: {stats['unique_today']} | "
                f"🖥 دسکتاپ: {stats['desktop']} | "
                f"📱 موبایل: {stats['mobile']} | "
                f"📲 تبلت: {stats['tablet']} | "
                f"📅 امروز: {stats['today']} | "
                f"📆 دیروز: {stats['yesterday']} | "
                f"🗓 هفته: {stats['week']} | "
                f"📈 ماه: {stats['month']} | "
                f"📊 سال: {stats['year']} | "
                f"📦 کل: {stats['total']}"
            ),
            level=messages.INFO,
        )

        return super().changelist_view(request, extra_context)