from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum

from .models import SalesReport


# =================================================
# Delete Button
# =================================================
def admin_delete_button(obj):
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete",
        args=[obj.pk],
    )
    return format_html(
        '<a href="{}" style="'
        'background:#d7263d;'
        'color:white;'
        'padding:6px 10px;'
        'border-radius:8px;'
        'text-decoration:none;'
        'font-weight:bold;'
        '">🗑 حذف</a>',
        url,
    )


admin_delete_button.short_description = "حذف"


# =================================================
# Filters (سال → ماه واقعی)
# =================================================
class JalaliYearFilter(admin.SimpleListFilter):
    title = "سال شمسی"
    parameter_name = "jalali_year"

    def lookups(self, request, model_admin):
        years = (
            SalesReport.objects
            .values_list("jalali_year", flat=True)
            .distinct()
            .order_by("-jalali_year")
        )
        return [(y, y) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(jalali_year=self.value())
        return queryset


class JalaliMonthFilter(admin.SimpleListFilter):
    title = "ماه شمسی"
    parameter_name = "jalali_month"

    def lookups(self, request, model_admin):
        year = request.GET.get("jalali_year")
        qs = SalesReport.objects.all()

        if year:
            qs = qs.filter(jalali_year=year)

        months = (
            qs.values_list("jalali_month", flat=True)
            .distinct()
            .order_by("jalali_month")
        )

        return [
            (m, dict(SalesReport.JalaliMonth.choices).get(m))
            for m in months
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(jalali_month=self.value())
        return queryset


# =================================================
# SalesReport Admin
# =================================================
@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    actions = None

    # ================================
    # List View
    # ================================
    list_display = (
        "jalali_date_display",
        "formatted_total_sales",
        "jalali_year_total_display",
        "created_at",
        "delete_button",
    )

    list_filter = (
        JalaliYearFilter,
        JalaliMonthFilter,
    )

    search_fields = (
        "jalali_year",
        "gregorian_year",
    )

    ordering = ("-jalali_year", "-jalali_month")

    readonly_fields = ("created_at",)

    # ================================
    # Form Layout
    # ================================
    fieldsets = (
        ("📅 تاریخ شمسی", {
            "fields": ("jalali_year", "jalali_month"),
        }),
        ("📆 تاریخ میلادی", {
            "fields": ("gregorian_year", "gregorian_month"),
        }),
        ("💰 اطلاعات فروش", {
            "fields": ("total_sales",),
        }),
        ("🕒 سیستم", {
            "fields": ("created_at",),
        }),
    )

    # ================================
    # Custom Columns
    # ================================
    def jalali_date_display(self, obj):
        return f"{obj.jalali_month_name} {obj.jalali_year}"

    jalali_date_display.short_description = "تاریخ شمسی"
    jalali_date_display.admin_order_field = "jalali_year"

    def formatted_total_sales(self, obj):
        return format_html(
            "<strong>{}</strong> تومان",
            f"{obj.total_sales:,}"
        )

    formatted_total_sales.short_description = "فروش ماه"

    def jalali_year_total_display(self, obj):
        total = SalesReport.yearly_total(obj.jalali_year)
        return format_html(
            "<span style='color:#0a7c2f;font-weight:bold'>{}</span> تومان",
            f"{total:,}"
        )

    jalali_year_total_display.short_description = "جمع سال (شمسی)"

    def delete_button(self, obj):
        return admin_delete_button(obj)
