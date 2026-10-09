# app_sale/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from .models import SalesReport
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core
from app_core.url_helpers import is_english_request


def sales_chart_view(request):
    """
    نمایش نمودار فروش + جدول گزارش‌ها (فارسی/انگلیسی)
    """
    is_english = is_english_request(request)

    # =================================================
    # همه گزارش‌ها (برای نمودار)
    # =================================================
    all_reports = (
        SalesReport.objects
        .all()
        .order_by("jalali_year", "jalali_month")  # ✅ صعودی برای نمودار
    )

    # =================================================
    # داده‌های نمودار
    # =================================================
    labels = [
        f"{r.jalali_month_name} {r.jalali_year}"
        for r in all_reports
    ]

    sales_data = [
        float(r.total_sales) if r.total_sales is not None else 0
        for r in all_reports
    ]

    # =================================================
    # گزارش‌ها برای جدول (نزولی — جدیدترین اول)
    # =================================================
    table_reports = (
        SalesReport.objects
        .all()
        .order_by("-jalali_year", "-jalali_month", "-created_at")
    )

    # =================================================
    # صفحه‌بندی جدول
    # =================================================
    paginator = Paginator(table_reports, 10)
    page = request.GET.get("page")

    try:
        reports_page = paginator.page(page)
    except PageNotAnInteger:
        reports_page = paginator.page(1)
    except EmptyPage:
        reports_page = paginator.page(paginator.num_pages)

    # =================================================
    # قالب بر اساس زبان
    # =================================================
    template_name = (
        "LTR/sale/sales-chart.html"
        if is_english
        else "RTL/sale/sale_chart.html"
    )

    # =================================================
    # Context
    # =================================================
    context = {
        "labels": labels,
        "sales_data": sales_data,
        "reports": reports_page,
        "total_reports": all_reports.count(),
        "seo": SEOManager.get_page("sale"),
        "is_english": is_english,
    }

    return render(request, template_name, context)