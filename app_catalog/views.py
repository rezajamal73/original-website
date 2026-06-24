# app_catalog/views.py
from django.shortcuts import render
from django.http import Http404
from django.db.models import Count, Q

from .models import CompanyCatalog
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo
from app_product.models import ProductCategory


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


def company_catalog_view(request):
    catalog = CompanyCatalog.objects.first()
    if not catalog:
        raise Http404("Catalog not found")

    context = {
        "catalog": catalog,
        **get_common_context(),
    }

    return render(request, "RTL/catalog/catalog.html", context)
