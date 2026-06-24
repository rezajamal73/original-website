# app_inquiry/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count

from app_product.models import ProductCategory
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo

from .models import PurchaseInquiry, InquiryTag


def get_common_context():
    """
    داده‌های مشترک تمام صفحات (دقیقاً مثل auction)
    """
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


def inquiry_home(request, slug=None):
    inquiries = (
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags")
    )

    # ✅ فیلتر بر اساس category slug
    if slug:
        inquiries = inquiries.filter(category__slug=slug)

    paginator = Paginator(inquiries, 8)
    page_number = request.GET.get("page")

    try:
        inquiries = paginator.get_page(page_number)
    except PageNotAnInteger:
        inquiries = paginator.get_page(1)
    except EmptyPage:
        inquiries = paginator.get_page(paginator.num_pages)

    context = {
        "inquiries": inquiries,
        **get_common_context(),
    }
    return render(request, "RTL/inquiry/inquiry-home.html", context)



def inquiry_single(request, pk):
    inquiry = get_object_or_404(
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags", "gallery_images"),
        pk=pk
    )

    context = {
        "inquiry": inquiry,
        **get_common_context(),
    }
    return render(request, "RTL/inquiry/inquiry-single.html", context)


def inquiry_tag(request, slug):
    tag = get_object_or_404(InquiryTag, slug=slug)

    inquiries = (
        PurchaseInquiry.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )

    paginator = Paginator(inquiries, 8)
    page_number = request.GET.get("page")

    try:
        inquiries = paginator.get_page(page_number)
    except PageNotAnInteger:
        inquiries = paginator.get_page(1)
    except EmptyPage:
        inquiries = paginator.get_page(paginator.num_pages)

    context = {
        "tag": tag,
        "inquiries": inquiries,
        **get_common_context(),
    }
    return render(request, "RTL/inquiry/inquiry-home.html", context)


def inquiry_search(request):
    s = request.GET.get("s", "").strip()

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

    paginator = Paginator(inquiries, 8)
    page_number = request.GET.get("page")

    try:
        inquiries = paginator.get_page(page_number)
    except PageNotAnInteger:
        inquiries = paginator.get_page(1)
    except EmptyPage:
        inquiries = paginator.get_page(paginator.num_pages)

    context = {
        "inquiries": inquiries,
        "search_query": s,
        **get_common_context(),
    }
    return render(request, "RTL/inquiry/inquiry-home.html", context)
