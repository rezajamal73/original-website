# app_tender_holding/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from .models import Holding, HoldingCategory, HoldingTag
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core
from app_core.url_helpers import is_english_request


# =====================================================
# CONTEXT HELPER
# =====================================================
def get_holding_context(is_english=False):
    """
    دسته‌بندی‌های هلدینگ برای سایدبار.
    """
    return {
        "holding_categories": (
            HoldingCategory.objects
            .prefetch_related("holdings")
            .order_by("order", "-created_at_fa")
        )
    }


# =====================================================
# PAGINATION HELPER
# =====================================================
def paginate_queryset(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.get_page(page_number)
    except PageNotAnInteger:
        return paginator.get_page(1)
    except EmptyPage:
        return paginator.get_page(paginator.num_pages)


# =====================================================
# TEMPLATE HELPER
# =====================================================
def _get_template(name, is_english):
    """
    انتخاب قالب بر اساس زبان.
    مثال: _get_template("tender-holding-home.html", True)
          → "LTR/tender_holding/tender-holding-home.html"
    """
    prefix = "LTR" if is_english else "RTL"
    return f"{prefix}/tender_holding/{name}"


# =====================================================
# HOLDING HOME (ALL / CATEGORY)
# =====================================================
def tender_holding_home(request, cat_name=None):
    """
    لیست هلدینگ‌ها
    - همه
    - یا فیلتر بر اساس دسته‌بندی
    """
    is_english = is_english_request(request)

    holdings_qs = (
        Holding.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    if cat_name:
        # ✅ فیلتر بر اساس زبان
        if is_english:
            holdings_qs = holdings_qs.filter(category__title_en=cat_name)
        else:
            holdings_qs = holdings_qs.filter(category__title_fa=cat_name)

    holdings = paginate_queryset(request, holdings_qs)

    context = {
        "holdings": holdings,
        "active_category": cat_name,
        "seo": SEOManager.get_page("tender_holding"),
        "is_english": is_english,
        **get_holding_context(is_english),
    }
    return render(
        request,
        _get_template("tender-holding-home.html", is_english),
        context,
    )


# =====================================================
# HOLDING SINGLE — با pid + slug
# =====================================================
def tender_holding_single(request, slug: str):
    """
    صفحه جزئیات یک هلدینگ

    فارسی:    /tender_holding/نام-هلدینگ/
    انگلیسی:  /en/tender_holding/holding-name/
    """
    is_english = is_english_request(request)

    if is_english:
        holding = get_object_or_404(
            Holding.objects
            .select_related("category")
            .prefetch_related("tags", "gallery_images"),
            slug_en=slug,
        )
    else:
        holding = get_object_or_404(
            Holding.objects
            .select_related("category")
            .prefetch_related("tags", "gallery_images"),
            slug=slug,
        )

    context = {
        "holding": holding,
        "seo": SEOManager.get_object(holding),
        "is_english": is_english,
        **get_holding_context(is_english),
    }

    return render(
        request,
        _get_template("tender-holding-single.html", is_english),
        context,
    )


# =====================================================
# HOLDING SINGLE REDIRECT — از URL قدیمی /tender_holding/5/
# =====================================================
def tender_holding_single_redirect(request, pid):
    """
    ریدایرکت از URL قدیمی (فقط pid) به URL جدید (pid + slug).
    """
    is_english = is_english_request(request)

    holding = get_object_or_404(Holding, pk=pid)

    if is_english:
        target = "app_tender_holding_en:tender_holding_single_en"
        redirect_slug = holding.slug_en or holding.slug
    else:
        target = "app_tender_holding:tender_holding_single"
        redirect_slug = holding.slug

    return redirect(target, pid=pid, slug=redirect_slug, permanent=True)


# =====================================================
# HOLDING SEARCH
# =====================================================
def tender_holding_search(request):
    """
    جستجو در هلدینگ‌ها
    """
    is_english = is_english_request(request)

    query = request.GET.get("s", "").strip()

    holdings_qs = Holding.objects.all()

    if query:
        holdings_qs = holdings_qs.filter(
            Q(title_fa__icontains=query) |
            Q(title_en__icontains=query) |
            Q(description_fa__icontains=query) |
            Q(description_en__icontains=query) |
            Q(call_number__icontains=query)
        )

    holdings = paginate_queryset(request, holdings_qs)

    context = {
        "holdings": holdings,
        "search_query": query,
        "seo": SEOManager.get_page("tender_holding"),
        "is_english": is_english,
        **get_holding_context(is_english),
    }
    return render(
        request,
        _get_template("tender-holding-home.html", is_english),
        context,
    )


# =====================================================
# HOLDING TAG
# =====================================================
def tender_holding_tag(request, slug):
    """
    نمایش هلدینگ‌ها بر اساس تگ
    """
    is_english = is_english_request(request)

    # ✅ انتخاب اسلاگ درست بر اساس زبان
    if is_english:
        tag = get_object_or_404(HoldingTag, slug_en=slug)
    else:
        tag = get_object_or_404(HoldingTag, slug=slug)

    holdings_qs = (
        Holding.objects
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    holdings = paginate_queryset(request, holdings_qs)

    context = {
        "tag": tag,
        "holdings": holdings,
        "seo": SEOManager.get_page("tender_holding"),
        "is_english": is_english,
        **get_holding_context(is_english),
    }
    return render(
        request,
        _get_template("tender-holding-home.html", is_english),
        context,
    )