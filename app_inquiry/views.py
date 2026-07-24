# app_inquiry/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from .models import PurchaseInquiry, InquiryTag
from app_seo.utils import SEOManager


# =====================================================
# INQUIRY HOME
# =====================================================

def inquiry_home(request, slug=None):

    inquiries = (
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags")
    )

    if slug:
        inquiries = inquiries.filter(
            category__slug=slug
        )

    paginator = Paginator(inquiries, 8)
    page_number = request.GET.get("page")

    try:
        inquiries = paginator.get_page(page_number)
    except PageNotAnInteger:
        inquiries = paginator.get_page(1)
    except EmptyPage:
        inquiries = paginator.get_page(
            paginator.num_pages
        )

    context = {
        "inquiries": inquiries,
        "seo": SEOManager.get_page("inquiry"),
    }

    return render(
        request,
        "RTL/inquiry/inquiry-home.html",
        context
    )


# =====================================================
# INQUIRY SINGLE
# =====================================================

def inquiry_single(request, pk):

    inquiry = get_object_or_404(
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related(
            "tags",
            "gallery_images"
        ),
        pk=pk
    )

    context = {
        "inquiry": inquiry,
        "seo": SEOManager.get_object(
            inquiry
        ),
    }

    return render(
        request,
        "RTL/inquiry/inquiry-single.html",
        context
    )


# =====================================================
# INQUIRY TAG
# =====================================================

def inquiry_tag(request, slug):

    tag = get_object_or_404(
        InquiryTag,
        slug=slug
    )

    inquiries = (
        PurchaseInquiry.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )

    paginator = Paginator(inquiries, 8)

    inquiries = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "tag": tag,
        "inquiries": inquiries,
        "seo": SEOManager.get_page(
            "inquiry_tag"
        ),
    }

    return render(
        request,
        "RTL/inquiry/inquiry-home.html",
        context
    )


# =====================================================
# INQUIRY SEARCH
# =====================================================

def inquiry_search(request):

    s = request.GET.get(
        "s",
        ""
    ).strip()

    inquiries = (
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags")
    )

    if s:
        inquiries = inquiries.filter(
            Q(title_fa__icontains=s)
            | Q(title_en__icontains=s)
            | Q(description_fa__icontains=s)
            | Q(description_en__icontains=s)
            | Q(inquiry_number__icontains=s)
        )

    paginator = Paginator(
        inquiries,
        8
    )

    inquiries = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "inquiries": inquiries,
        "search_query": s,
        "seo": SEOManager.get_page(
            "inquiry_search"
        ),
    }

    return render(
        request,
        "RTL/inquiry/inquiry-home.html",
        context
    )