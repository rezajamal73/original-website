# app_auction/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from app_product.models import ProductCategory
from django.db.models import Count, Q
from app_auction.models import Auction, AuctionTag
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo


def get_common_context():
    """
    داده‌های مشترک تمام صفحات
    """
    return {    "categories": (
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
        )
    }


def auction_home(request, cat_name=None):
    auctions = (
        Auction.objects
        .select_related("category")
        .prefetch_related("tags")
    )  # ❗ هیچ order_by نذار

    if cat_name:
        auctions = auctions.filter(category__title_fa=cat_name)

    paginator = Paginator(auctions, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    context = {
        "auctions": auctions,
        **get_common_context(),
    }
    return render(request, "RTL/auction/auction-home.html", context)



def auction_single(request, pid):
    auction = get_object_or_404(
        Auction.objects
        .select_related("category",)
        .prefetch_related("tags", "gallery_images"),
        pk=pid
    )

    context = {
        "auction": auction,
        **get_common_context(),
    }
    return render(request, "RTL/auction/auction-single.html", context)


def auction_search(request):
    auctions = (
        Auction.objects.all()
        .select_related("category",)
        .prefetch_related("tags")
    )

    s = request.GET.get("s", "").strip()

    if s:
        auctions = auctions.filter(
            models.Q(description_fa__icontains=s)
            | models.Q(description_en__icontains=s)
            | models.Q(title_fa__icontains=s)
            | models.Q(title_en__icontains=s)
            | models.Q(call_number__icontains=s)
        )

    paginator = Paginator(auctions, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    context = {
        "auctions": auctions,
        "search_query": s,
        **get_common_context(),
    }
    return render(request, "RTL/auction/auction-home.html", context)

def auction_tag(request, slug):
    tag = get_object_or_404(AuctionTag, slug=slug)

    auctions = (
        Auction.objects.filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )  # ❗ بدون order_by تا Meta اعمال شود

    paginator = Paginator(auctions, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    context = {
        "tag": tag,
        "auctions": auctions,
        **get_common_context(),
    }
    return render(request, "RTL/auction/auction-home.html", context)
