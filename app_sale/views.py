from django.shortcuts import render

from .models import SalesReport
from app_seo.utils import SEOManager

# -------------------------------------------------
#  گزارش فروش (نمودار)
# -------------------------------------------------
def sales_chart_view(request):
    """
    Displays monthly sales chart (Jalali-based).
    """

    reports = (
        SalesReport.objects
        .all()
        .order_by("jalali_year", "jalali_month")
    )

    labels = [
        f"{r.jalali_month_name} {r.jalali_year}"
        for r in reports
    ]

    sales_data = [
        float(r.total_sales)
        for r in reports
    ]

    context = {
        "labels": labels,
        "sales_data": sales_data,
        "seo": SEOManager.get_page("sale"),
    }

    return render(request, "RTL/sale/sale_chart.html", context)
