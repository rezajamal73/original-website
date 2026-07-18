from datetime import timedelta
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.formats import date_format
from django.db.models import Count, Q
from django.http import HttpResponse
import csv

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    # تنظیمات نمایش
    list_display = (
        "ip",
        "path",
        "method",
        "formatted_date",
        "visit_count",
        "is_bot_badge",
        "last_seen_relative",
    )

    list_display_links = ("ip", "path")

    search_fields = (
        "ip",
        "path",
        "user_agent",
        "referer",
    )

    list_filter = (
        "created_at",
        "is_bot",
        "method",
        ("created_at", admin.DateFieldListFilter),
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    # فیلدهای فقط خواندنی
    readonly_fields = (
        "ip",
        "path",
        "method",
        "user_agent",
        "referer",
        "created_at",
        "last_seen",
        "visit_count",
        "is_bot",
    )

    # اکشن‌های سفارشی
    actions = ["export_as_csv", "mark_as_bot", "unmark_as_bot"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # فقط سوپرادمین می‌تواند حذف کند
        return request.user.is_superuser

    # متدهای نمایش
    @admin.display(description="زمان بازدید", ordering="created_at")
    def formatted_date(self, obj):
        return date_format(obj.created_at, "Y/m/d H:i:s")

    @admin.display(description="آخرین فعالیت", ordering="last_seen")
    def last_seen_relative(self, obj):
        delta = timezone.now() - obj.last_seen
        if delta < timedelta(minutes=1):
            return "هم اکنون"
        elif delta < timedelta(hours=1):
            return f"{delta.seconds // 60} دقیقه قبل"
        elif delta < timedelta(days=1):
            return f"{delta.seconds // 3600} ساعت قبل"
        else:
            return date_format(obj.last_seen, "Y/m/d H:i")

    @admin.display(description="ربات", boolean=True)
    def is_bot_badge(self, obj):
        return obj.is_bot

    # اکشن‌ها
    @admin.action(description="خروجی CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=visits_export.csv'

        writer = csv.writer(response)
        writer.writerow([
            'IP', 'Path', 'Method', 'User Agent',
            'Referer', 'Created At', 'Last Seen',
            'Visit Count', 'Is Bot'
        ])

        for visit in queryset:
            writer.writerow([
                visit.ip,
                visit.path,
                visit.method,
                visit.user_agent[:100],
                visit.referer,
                visit.created_at,
                visit.last_seen,
                visit.visit_count,
                visit.is_bot,
            ])

        self.message_user(
            request,
            f"{queryset.count()} رکورد با موفقیت خروجی گرفتند.",
            level=messages.SUCCESS,
        )
        return response

    @admin.action(description="علامت‌گذاری به عنوان ربات")
    def mark_as_bot(self, request, queryset):
        updated = queryset.update(is_bot=True)
        self.message_user(
            request,
            f"{updated} بازدید به عنوان ربات علامت‌گذاری شدند.",
            level=messages.SUCCESS,
        )

    @admin.action(description="لغو علامت ربات")
    def unmark_as_bot(self, request, queryset):
        updated = queryset.update(is_bot=False)
        self.message_user(
            request,
            f"علامت ربات از {updated} بازدید برداشته شد.",
            level=messages.SUCCESS,
        )

    # آمار در changelist
    def get_visit_stats(self):
        now = timezone.now()
        today = now.date()

        qs = Visit.objects

        return {
            "online": qs.filter(
                last_seen__gte=now - timedelta(minutes=5)
            ).count(),

            "today": qs.filter(
                created_at__date=today
            ).count(),

            "yesterday": qs.filter(
                created_at__date=today - timedelta(days=1)
            ).count(),

            "week": qs.filter(
                created_at__gte=now - timedelta(days=7)
            ).count(),

            "month": qs.filter(
                created_at__gte=now - timedelta(days=30)
            ).count(),

            "year": qs.filter(
                created_at__gte=now - timedelta(days=365)
            ).count(),

            "total": qs.count(),

            "unique_today": qs.filter(
                created_at__date=today
            ).values('ip').distinct().count(),
        }

    def changelist_view(self, request, extra_context=None):
        stats = self.get_visit_stats()

        # نمایش آمار با فرمت بهتر
        message = (
            f"🟢 آنلاین: {stats['online']} | "
            f"📅 امروز: {stats['today']} | "
            f"👤 بازدیدکننده‌های امروز: {stats['unique_today']} | "
            f"📆 دیروز: {stats['yesterday']} | "
            f"🗓 هفته: {stats['week']} | "
            f"📈 ماه: {stats['month']} | "
            f"📊 سال: {stats['year']} | "
            f"📦 کل: {stats['total']}"
        )

        self.message_user(
            request,
            message,
            level=messages.INFO,
        )

        return super().changelist_view(request, extra_context)