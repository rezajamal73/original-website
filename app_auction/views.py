# app_auction/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models

from app_auction.models import Auction, AuctionTag
from app_seo.utils import SEOManager



# =====================================================
# AUCTION HOME
# =====================================================
def auction_home(request, cat_name=None):

    auctions_queryset = (
        Auction.objects
        .select_related("category")
        .prefetch_related("tags")
    )


    if cat_name:
        auctions_queryset = auctions_queryset.filter(
            category__title_fa=cat_name
        )


    paginator = Paginator(
        auctions_queryset,
        8
    )

    page_number = request.GET.get("page")


    try:
        auctions = paginator.get_page(page_number)

    except PageNotAnInteger:
        auctions = paginator.get_page(1)

    except EmptyPage:
        auctions = paginator.get_page(
            paginator.num_pages
        )


    context = {
        "auctions": auctions,
        "seo": SEOManager.get_page("auction"),
    }


    return render(
        request,
        "RTL/auction/auction-home.html",
        context
    )



# =====================================================
# AUCTION SINGLE
# =====================================================
def auction_single(request, pid):

    auction = get_object_or_404(
        Auction.objects
        .select_related("category")
        .prefetch_related(
            "tags",
            "gallery_images"
        ),
        pk=pid
    )


    context = {
        "auction": auction,
        "seo": SEOManager.get_object(auction),
    }


    return render(
        request,
        "RTL/auction/auction-single.html",
        context
    )



# =====================================================
# AUCTION SEARCH
# =====================================================
def auction_search(request):

    auctions_queryset = (
        Auction.objects
        .select_related("category")
        .prefetch_related("tags")
    )


    s = request.GET.get(
        "s",
        ""
    ).strip()


    if s:
        auctions_queryset = auctions_queryset.filter(

            models.Q(description_fa__icontains=s)
            |
            models.Q(description_en__icontains=s)
            |
            models.Q(title_fa__icontains=s)
            |
            models.Q(title_en__icontains=s)
            |
            models.Q(call_number__icontains=s)

        )


    paginator = Paginator(
        auctions_queryset,
        8
    )

    page_number = request.GET.get("page")


    try:
        auctions = paginator.get_page(page_number)

    except PageNotAnInteger:
        auctions = paginator.get_page(1)

    except EmptyPage:
        auctions = paginator.get_page(
            paginator.num_pages
        )


    context = {
        "auctions": auctions,
        "search_query": s,
        "seo": SEOManager.get_page("auction"),
    }


    return render(
        request,
        "RTL/auction/auction-home.html",
        context
    )



# =====================================================
# AUCTION TAG
# =====================================================
def auction_tag(request, slug):

    tag = get_object_or_404(
        AuctionTag,
        slug=slug
    )


    auctions_queryset = (
        Auction.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )


    paginator = Paginator(
        auctions_queryset,
        8
    )

    page_number = request.GET.get("page")


    try:
        auctions = paginator.get_page(page_number)

    except PageNotAnInteger:
        auctions = paginator.get_page(1)

    except EmptyPage:
        auctions = paginator.get_page(
            paginator.num_pages
        )


    context = {
        "tag": tag,
        "auctions": auctions,
        "seo": SEOManager.get_page("auction"),
    }


    return render(
        request,
        "RTL/auction/auction-home.html",
        context
    )