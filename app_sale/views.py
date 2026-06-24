from django.shortcuts import render
from django.db.models import Count, Q

from .models import SalesReport
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo
from app_product.models import ProductCategory


# -------------------------------------------------
#  Context مشترک (مشابه الگوی پروژه)
# -------------------------------------------------
def get_common_context():
    return {
        "categories": (
            ProductCategory.objects
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__status="published")
                )
            )
            .filter(product_count__gt=0)
            .order_by("priority", "title_fa")
        ),
        "site_info": SiteMainInfo.objects.first(),
        "banner": OtherBanner.objects.filter(status="published").first(),
        "follow_links": (
            FollowUsLink.objects
            .filter(is_active=True, svg_icon__isnull=False)
            .exclude(url="")
            .order_by("display_order")
        ),
    }


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
        **get_common_context(),
    }

    return render(request, "RTL/sale/sale_chart.html", context)
