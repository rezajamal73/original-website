from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from .models import SalesReport
from app_seo.utils import SEOManager


def sales_chart_view(request):
    reports = (
        SalesReport.objects
        .all()
        .order_by("-jalali_year", "-jalali_month", "-created_at")
    )

    # داده‌های نمودار
    labels = [
        f"{r.jalali_month_name} {r.jalali_year}"
        for r in reports
    ]

    sales_data = [
        float(r.total_sales)
        for r in reports
    ]

    # صفحه‌بندی جدول
    paginator = Paginator(reports, 10)   # هر صفحه 10 رکورد
    page = request.GET.get("page")

    try:
        reports_page = paginator.page(page)
    except PageNotAnInteger:
        reports_page = paginator.page(1)
    except EmptyPage:
        reports_page = paginator.page(paginator.num_pages)

    context = {
        "labels": labels,
        "sales_data": sales_data,
        "reports": reports_page,
        "seo": SEOManager.get_page("sale"),
    }

    return render(request, "RTL/sale/sale_chart.html", context)