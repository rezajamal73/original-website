# app/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from app_product.models import ProductCategory
from django.db.models import Count, Q
from .models import Media
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo


# ------------------------------------------------------
#   COMMON CONTEXT
# ------------------------------------------------------
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
        .order_by("priority", "title_fa")),
        "site_info": SiteMainInfo.objects.first(),
        "banner": OtherBanner.objects.filter(status="published").first(),
        "follow_links": (
            FollowUsLink.objects
            .filter(is_active=True, svg_icon__isnull=False)
            .exclude(url="")
            .order_by("display_order")
        ),
    }


# ------------------------------------------------------
#   MEDIA HOME (LIST)
# ------------------------------------------------------
def media_home(request):
    media_queryset = (
        Media.objects
        .filter(status="published")   # ✅ فیلتر صحیح بر اساس مدل
        .prefetch_related("images", "videos")
        .order_by("order")
    )
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
    paginator = Paginator(media_queryset, 6)
    page_number = request.GET.get("page")
    media_sections = paginator.get_page(page_number)

    context = {
        "media_sections": media_sections,
        **get_common_context(),
    }

    return render(
        request,
        "RTL/media/media_home.html",
        context,
    )


# ------------------------------------------------------
#   MEDIA SINGLE
# ------------------------------------------------------
def media_single(request, pk):
    media = get_object_or_404(
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos"),
        pk=pk,
    )
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
    context = {
        "media": media,
        "images": media.images.all(),   # ✅ مدل is_active ندارد
        "videos": media.videos.all(),   # ✅ مدل is_active ندارد
        **get_common_context(),
    }

    return render(
        request,
        "RTL/media/media_single.html",
        context,
    )
