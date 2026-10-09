# app_inquiry/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from .models import PurchaseInquiry, InquiryTag
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core
from app_core.url_helpers import is_english_request


# =====================================================
# TEMPLATE HELPER
# =====================================================
def _get_template(name, is_english):
    """
    انتخاب قالب بر اساس زبان.
    """
    prefix = "LTR" if is_english else "RTL"
    return f"{prefix}/inquiry/{name}"


# =====================================================
# PAGINATION HELPER
# =====================================================
def _paginate(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.get_page(page_number)
    except PageNotAnInteger:
        return paginator.get_page(1)
    except EmptyPage:
        return paginator.get_page(paginator.num_pages)


# =====================================================
# INQUIRY HOME
# =====================================================
def inquiry_home(request, slug=None):
    """
    لیست استعلام‌ها (همه / بر اساس دسته‌بندی)
    """
    is_english = is_english_request(request)

    inquiries_qs = (
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    if slug:
        # ✅ فیلتر بر اساس زبان
        if is_english:
            inquiries_qs = inquiries_qs.filter(category__slug_en=slug)
        else:
            inquiries_qs = inquiries_qs.filter(category__slug=slug)

    inquiries = _paginate(request, inquiries_qs)

    context = {
        "inquiries": inquiries,
        "active_category_slug": slug,
        "seo": SEOManager.get_page("inquiry"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("inquiry-home.html", is_english),
        context,
    )


# =====================================================
# INQUIRY SINGLE — با pid + slug
# =====================================================
def inquiry_single(request, pid, slug=None):
    """
    صفحه جزئیات یک استعلام
    """
    is_english = is_english_request(request)

    inquiry = get_object_or_404(
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags", "gallery_images"),
        pk=pid,
    )

    # ✅ اگه slug داده شده، بررسی کن
    if slug:
        correct_slug = inquiry.slug_en if is_english else inquiry.slug

        if correct_slug != slug:
            target = (
                "app_inquiry_en:inquiry_single_en"
                if is_english
                else "app_inquiry:inquiry_single"
            )
            return redirect(
                target,
                pid=pid,
                slug=correct_slug,
                permanent=True,
            )

    context = {
        "inquiry": inquiry,
        "seo": SEOManager.get_object(inquiry),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("inquiry-single.html", is_english),
        context,
    )


# =====================================================
# INQUIRY SINGLE REDIRECT — از URL قدیمی /inquiry/5/
# =====================================================
def inquiry_single_redirect(request, pid):
    """
    ریدایرکت از URL قدیمی (فقط pid) به URL جدید (pid + slug).
    """
    is_english = is_english_request(request)

    inquiry = get_object_or_404(PurchaseInquiry, pk=pid)

    if is_english:
        target = "app_inquiry_en:inquiry_single_en"
        redirect_slug = inquiry.slug_en or inquiry.slug
    else:
        target = "app_inquiry:inquiry_single"
        redirect_slug = inquiry.slug

    return redirect(
        target,
        pid=pid,
        slug=redirect_slug,
        permanent=True,
    )


# =====================================================
# INQUIRY TAG
# =====================================================
def inquiry_tag(request, slug):
    """
    نمایش استعلام‌ها بر اساس تگ
    """
    is_english = is_english_request(request)

    # ✅ انتخاب اسلاگ درست بر اساس زبان
    if is_english:
        tag = get_object_or_404(InquiryTag, slug_en=slug)
    else:
        tag = get_object_or_404(InquiryTag, slug=slug)

    inquiries_qs = (
        PurchaseInquiry.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    inquiries = _paginate(request, inquiries_qs)

    context = {
        "tag": tag,
        "inquiries": inquiries,
        "seo": SEOManager.get_page("inquiry"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("inquiry-home.html", is_english),
        context,
    )


# =====================================================
# INQUIRY SEARCH
# =====================================================
def inquiry_search(request):
    """
    جستجو در استعلام‌ها
    """
    is_english = is_english_request(request)

    s = request.GET.get("s", "").strip()

    inquiries_qs = (
        PurchaseInquiry.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    if s:
        inquiries_qs = inquiries_qs.filter(
            Q(title_fa__icontains=s)
            | Q(title_en__icontains=s)
            | Q(description_fa__icontains=s)
            | Q(description_en__icontains=s)
            | Q(inquiry_number__icontains=s)
        )

    inquiries = _paginate(request, inquiries_qs)

    context = {
        "inquiries": inquiries,
        "search_query": s,
        "seo": SEOManager.get_page("inquiry"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("inquiry-home.html", is_english),
        context,
    )