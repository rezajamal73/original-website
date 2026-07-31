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
        "method",
        "visit_count",
        "formatted_date",
        "last_seen_relative",
        "is_bot_badge",
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
    )

    list_filter = (
        ("created_at", admin.DateFieldListFilter),
        "is_bot",
        "method",
    )

    readonly_fields = (
        "ip",
        "page",
        "path",
        "method",
        "user_agent",
        "referer",
        "created_at_j",
        "last_seen_j",
        "visit_count",
        "is_bot",
    )

    ordering = ("-created_at",)

    # ------------------------
    # Pagination
    # ------------------------
    list_per_page = 50          # هر صفحه ۱۰ رکورد
    list_max_show_all = 50      # گزینه «نمایش همه» بعد از ۱۰ رکورد غیرفعال می‌شود

    date_hierarchy = "created_at"

    actions = (
        "export_as_csv",
        "mark_as_bot",
        "unmark_as_bot",
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

    @admin.display(boolean=True, description="ربات")
    def is_bot_badge(self, obj):
        return obj.is_bot

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
            "Method",
            "Visit Count",
            "Bot",
            "First Visit",
            "Last Activity",
        ])

        for visit in queryset:
            writer.writerow([
                visit.ip,
                visit.page_name,
                visit.path,
                visit.method,
                visit.visit_count,
                "Yes" if visit.is_bot else "No",
                visit.created_at_j,
                visit.last_seen_j,
            ])

        self.message_user(
            request,
            f"{queryset.count()} رکورد با موفقیت خروجی گرفته شد.",
            level=messages.SUCCESS,
        )

        return response

    @admin.action(description="علامت‌گذاری به عنوان ربات")
    def mark_as_bot(self, request, queryset):

        updated = queryset.update(is_bot=True)

        self.message_user(
            request,
            f"{updated} رکورد بروزرسانی شد.",
            level=messages.SUCCESS,
        )

    @admin.action(description="لغو علامت ربات")
    def unmark_as_bot(self, request, queryset):

        updated = queryset.update(is_bot=False)

        self.message_user(
            request,
            f"{updated} رکورد بروزرسانی شد.",
            level=messages.SUCCESS,
        )

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

            "today": self._sum(
                qs.filter(created_at__date=today)
            ),

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
        }

    # ------------------------

    def changelist_view(self, request, extra_context=None):

        stats = self.get_visit_stats()

        self.message_user(
            request,
            (
                f"🟢 آنلاین: {stats['online']} | "
                f"👤 بازدیدکننده یکتا: {stats['unique_today']} | "
                f"📅 امروز: {stats['today']} | "
                f"📆 دیروز: {stats['yesterday']} | "
                f"🗓 هفته: {stats['week']} | "
                f"📈 ماه: {stats['month']} | "
                f"📊 سال: {stats['year']} | "
                f"📦 کل بازدیدها: {stats['total']}"
            ),
            level=messages.INFO,
        )

        return super().changelist_view(request, extra_context)