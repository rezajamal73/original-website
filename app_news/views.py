from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from app_news.models import News, NewsCategory, NewsTag
from app_seo.utils import SEOManager


# =====================================================
# NEWS HOME
# =====================================================

def news_home(request, cat_slug=None):

    news_queryset = (
        News.objects
        .filter(status="published")
        .select_related("category")
        .prefetch_related("tags")
    )

    if cat_slug:
        news_queryset = news_queryset.filter(
            category__slug=cat_slug
        )

    paginator = Paginator(news_queryset, 8)
    page_number = request.GET.get("page")

    try:
        news_list = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        news_list = paginator.get_page(1)

    context = {
        "news_list": news_list,
        "categories_2": (
            NewsCategory.objects
            .filter(news__status="published")
            .distinct()
        ),
        "seo": SEOManager.get_page("news"),
    }

    return render(
        request,
        "RTL/news/news_home.html",
        context
    )


# =====================================================
# NEWS SINGLE
# =====================================================

def news_single(request, pid):

    news = get_object_or_404(
        News.objects
        .filter(status="published")
        .select_related("category")
        .prefetch_related("tags", "videos"),
        pk=pid
    )

    context = {
        "news": news,
        "videos": news.videos.all(),
        "seo": SEOManager.get_object(news),
    }

    return render(
        request,
        "RTL/news/news_single.html",
        context
    )


# =====================================================
# NEWS TAG
# =====================================================

def news_tag(request, slug):

    tag = get_object_or_404(
        NewsTag,
        slug=slug
    )

    news_queryset = (
        News.objects
        .filter(
            status="published",
            tags=tag
        )
        .select_related("category")
        .prefetch_related("tags")
    )

    paginator = Paginator(news_queryset, 8)
    news_list = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "tag": tag,
        "news_list": news_list,
        "seo": SEOManager.get_page("news"),
    }

    return render(
        request,
        "RTL/news/news_home.html",
        context
    )


# =====================================================
# NEWS CATEGORY
# =====================================================

def news_category(request, slug):

    category = get_object_or_404(
        NewsCategory,
        slug=slug
    )

    news_queryset = (
        News.objects
        .filter(
            status="published",
            category=category
        )
        .select_related("category")
        .prefetch_related("tags")
    )

    paginator = Paginator(news_queryset, 8)
    news_list = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "category": category,
        "news_list": news_list,
        "seo": SEOManager.get_page("news"),
    }

    return render(
        request,
        "RTL/news/news_home.html",
        context
    )