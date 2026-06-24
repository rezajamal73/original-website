from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app_product.models import ProductCategory
from django.db.models import Count, Q
from app_news.models import News, NewsCategory, NewsTag
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink
from app_reports.models import SiteMainInfo


# =====================================================
# COMMON CONTEXT
# =====================================================
def get_common_context():
    """
    داده‌های عمومی مشترک در تمام صفحات اخبار
    """
    site_info = SiteMainInfo.objects.first()

    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True, svg_icon__isnull=False)
        .exclude(url="")
        .order_by("display_order")
    )

    banner = OtherBanner.objects.filter(status="published").first()

    categories_2 = NewsCategory.objects.filter(
        news__status="published"
    ).distinct()

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
        "site_info": site_info,
        "follow_links": follow_links,
        "banner": banner,
        "categories_2": categories_2,
    }


# =====================================================
# NEWS HOME
# =====================================================
def news_home(request, cat_slug=None,):
    news_queryset = (
        News.objects.filter(status="published")
        .select_related("category")
        .prefetch_related("tags")
    )

    if cat_slug:
        news_queryset = news_queryset.filter(category__slug=cat_slug)


    paginator = Paginator(news_queryset, 8)
    page_number = request.GET.get("page")

    try:
        news_list = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        news_list = paginator.get_page(1)

    context = {
        **get_common_context(),
        "news_list": news_list,
    }

    return render(request, "RTL/news/news_home.html", context)


# =====================================================
# NEWS SINGLE
# =====================================================
def news_single(request, pid):
    news = get_object_or_404(
        News.objects.filter(status="published")
        .select_related( "category")
        .prefetch_related("tags", "videos"),
        pk=pid
    )

    context = {
        **get_common_context(),
        "news": news,
        "videos": news.videos.all(),
    }

    return render(request, "RTL/news/news_single.html", context)


# =====================================================
# NEWS TAG
# =====================================================
def news_tag(request, slug):
    tag = get_object_or_404(NewsTag, slug=slug)

    news_queryset = (
        News.objects.filter(status="published", tags=tag)
        .select_related("category")
        .prefetch_related("tags")
    )

    paginator = Paginator(news_queryset, 8)
    page_number = request.GET.get("page")

    try:
        news_list = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        news_list = paginator.get_page(1)

    context = {
        **get_common_context(),
        "tag": tag,
        "news_list": news_list,
    }

    return render(request, "RTL/news/news_home.html", context)


# =====================================================
# NEWS CATEGORY
# =====================================================
def news_category(request, slug):
    category = get_object_or_404(NewsCategory, slug=slug)

    news_queryset = (
        News.objects.filter(status="published", category=category)
        .select_related( "category")
        .prefetch_related("tags")
    )

    paginator = Paginator(news_queryset, 8)
    page_number = request.GET.get("page")

    try:
        news_list = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        news_list = paginator.get_page(1)

    context = {
        **get_common_context(),
        "category": category,
        "news_list": news_list,
    }

    return render(request, "RTL/news/news_home.html", context)
