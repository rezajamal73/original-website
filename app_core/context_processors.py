# app_core/context_processors.py

from django.db.models import Count, Q

from app_product.models import ProductCategory
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo


def common_context(request):
    """
    داده‌های مشترک کل سایت:
    منو، فوتر، اطلاعات سایت، بنر
    """

    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    site_info = SiteMainInfo.objects.first()

    banner = (
        OtherBanner.objects
        .filter(status="published")
        .first()
    )

    follow_links = (
        FollowUsLink.objects
        .filter(
            is_active=True,
            svg_icon__isnull=False
        )
        .exclude(url="")
        .order_by("display_order")
    )

    return {
        "categories": categories,
        "site_info": site_info,
        "banner": banner,
        "follow_links": follow_links,
    }