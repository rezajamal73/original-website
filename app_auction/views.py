# app_auction/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from app_auction.models import Auction, AuctionTag
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core
from app_core.url_helpers import is_english_request


# =====================================================
# AUCTION HOME
# =====================================================

def auction_home(request, cat_name=None):

    is_english = is_english_request(request)

    auctions_queryset = (
        Auction.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    if cat_name:
        if is_english:
            auctions_queryset = auctions_queryset.filter(
                category__title_en=cat_name
            )
        else:
            auctions_queryset = auctions_queryset.filter(
                category__title_fa=cat_name
            )

    paginator = Paginator(auctions_queryset, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    template_name = (
        "LTR/auction/auction-home.html"
        if is_english
        else "RTL/auction/auction-home.html"
    )

    context = {
        "auctions": auctions,
        "seo": SEOManager.get_page("auction"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# AUCTION SINGLE — ✅ بدون pid
# =====================================================

def auction_single(request, slug: str):
    """
    فارسی:    /auction/نام-مزایده/
    انگلیسی:  /en/auction/auction-name/
    """
    is_english = is_english_request(request)

    if is_english:
        auction = get_object_or_404(
            Auction.objects
            .select_related("category")
            .prefetch_related("tags", "gallery_images"),
            slug_en=slug,
        )
    else:
        auction = get_object_or_404(
            Auction.objects
            .select_related("category")
            .prefetch_related("tags", "gallery_images"),
            slug=slug,
        )

    template_name = (
        "LTR/auction/auction-single.html"
        if is_english
        else "RTL/auction/auction-single.html"
    )

    context = {
        "auction": auction,
        "seo": SEOManager.get_object(auction),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# AUCTION SEARCH
# =====================================================

def auction_search(request):

    is_english = is_english_request(request)

    auctions_queryset = (
        Auction.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    s = request.GET.get("s", "").strip()

    if s:
        auctions_queryset = auctions_queryset.filter(
            Q(description_fa__icontains=s)
            | Q(description_en__icontains=s)
            | Q(title_fa__icontains=s)
            | Q(title_en__icontains=s)
            | Q(call_number__icontains=s)
        )

    paginator = Paginator(auctions_queryset, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    template_name = (
        "LTR/auction/auction-home.html"
        if is_english
        else "RTL/auction/auction-home.html"
    )

    context = {
        "auctions": auctions,
        "search_query": s,
        "seo": SEOManager.get_page("auction"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# AUCTION TAG
# =====================================================

def auction_tag(request, slug):

    is_english = is_english_request(request)

    if is_english:
        tag = get_object_or_404(AuctionTag, slug_en=slug)
    else:
        tag = get_object_or_404(AuctionTag, slug=slug)

    auctions_queryset = (
        Auction.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    paginator = Paginator(auctions_queryset, 8)
    page_number = request.GET.get("page")

    try:
        auctions = paginator.get_page(page_number)
    except PageNotAnInteger:
        auctions = paginator.get_page(1)
    except EmptyPage:
        auctions = paginator.get_page(paginator.num_pages)

    template_name = (
        "LTR/auction/auction-home.html"
        if is_english
        else "RTL/auction/auction-home.html"
    )

    context = {
        "tag": tag,
        "auctions": auctions,
        "seo": SEOManager.get_page("auction"),
        "is_english": is_english,
    }

    return render(request, template_name, context)