from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .models import Holding, HoldingCategory, HoldingTag
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo

# =====================================================
# COMMON CONTEXT
# =====================================================
def get_common_context():
    """
    داده‌های عمومی مشترک برای صفحات هلدینگ
    """
    site_info = SiteMainInfo.objects.first()

    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True, svg_icon__isnull=False)
        .exclude(url="")
        .order_by("display_order")
    )

    banner = OtherBanner.objects.filter(status="published").first()

    categories = (
        HoldingCategory.objects
        .prefetch_related("holdings")
        .order_by("order", "-created_at_fa")
    )

    return {
        "categories": categories,
        "site_info": site_info,
        "banner": banner,
        "follow_links": follow_links,
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
# HOLDING HOME (ALL / CATEGORY)
# =====================================================
def tender_holding_home(request, cat_name=None):
    """
    لیست هلدینگ‌ها
    - همه
    - یا فیلتر بر اساس دسته‌بندی
    """
    holdings_qs = (
        Holding.objects
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at_fa")
    )

    if cat_name:
        holdings_qs = holdings_qs.filter(category__title_fa=cat_name)

    holdings = paginate_queryset(request, holdings_qs)

    context = {
        **get_common_context(),
        "holdings": holdings,
        "active_category": cat_name,
    }
    return render(request, "RTL/tender_holding/tender-holding-home.html", context)

# =====================================================
# HOLDING SINGLE
# =====================================================
def tender_holding_single(request, pid):
    """
    صفحه جزئیات یک هلدینگ
    """
    holding = get_object_or_404(
        Holding.objects
        .select_related("category")
        .prefetch_related("tags", "gallery_images"),
        pk=pid
    )

    context = {
        **get_common_context(),
        "holding": holding,
    }
    return render(request, "RTL/tender_holding/tender-holding-single.html", context)

# =====================================================
# HOLDING SEARCH
# =====================================================
def tender_holding_search(request):
    """
    جستجو در هلدینگ‌ها
    """
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
        **get_common_context(),
        "holdings": holdings,
        "search_query": query,
    }
    return render(request, "RTL/tender_holding/tender-holding-home.html", context)

# =====================================================
# HOLDING TAG
# =====================================================
def tender_holding_tag(request, slug):
    """
    نمایش هلدینگ‌ها بر اساس تگ
    """
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
        **get_common_context(),
        "tag": tag,
        "holdings": holdings,
    }
    return render(request, "RTL/tender_holding/tender-holding-home.html", context)
