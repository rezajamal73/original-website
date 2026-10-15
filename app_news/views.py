# app_news/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404

from app_news.models import News, NewsCategory, NewsTag
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
    return f"{prefix}/news/{name}"


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
# CATEGORIES HELPER  ← ✅ جدید
# =====================================================
def _get_categories_2():
    """
    دسته‌بندی‌هایی که حداقل یک خبر منتشرشده دارند.
    """
    return (
        NewsCategory.objects
        .filter(news__status="published")
        .distinct()
        .order_by("id")
    )


# =====================================================
# NEWS HOME
# =====================================================
def news_home(request, slug=None):
    """
    لیست اخبار (همه / بر اساس دسته‌بندی)
    """
    is_english = is_english_request(request)

    news_queryset = (
        News.objects
        .filter(status="published")
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-publish_date_fa", "-id")
    )

    if slug:
        # ✅ فیلتر بر اساس زبان
        if is_english:
            news_queryset = news_queryset.filter(category__slug_en=slug)
        else:
            news_queryset = news_queryset.filter(category__slug=slug)

    news_list = _paginate(request, news_queryset)

    context = {
        "news_list": news_list,
        "active_category_slug": slug,
        "categories_2": _get_categories_2(),   # ✅
        "seo": SEOManager.get_page("news"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("news_home.html", is_english),
        context,
    )


# =====================================================
# NEWS SINGLE — با slug
# =====================================================
def news_single(request, slug: str):
    """
    فارسی:    /news/عنوان-خبر/
    انگلیسی:  /en/news/news-title/
    """
    is_english = is_english_request(request)

    if is_english:
        news = get_object_or_404(
            News.objects
            .filter(status="published")
            .select_related("category")
            .prefetch_related("tags", "videos"),
            slug_en=slug,
        )
    else:
        news = get_object_or_404(
            News.objects
            .filter(status="published")
            .select_related("category")
            .prefetch_related("tags", "videos"),
            slug=slug,
        )

    template_name = (
        "LTR/news/news_single.html"
        if is_english
        else "RTL/news/news_single.html"
    )

    context = {
        "news": news,
        "videos": news.videos.all(),
        "seo": SEOManager.get_object(news),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# NEWS SINGLE REDIRECT — از URL قدیمی /news/5/
# =====================================================
def news_single_redirect(request, pid):
    """
    ریدایرکت از URL قدیمی (فقط pid) به URL جدید (slug).
    """
    is_english = is_english_request(request)

    news = get_object_or_404(News, pk=pid)

    if is_english:
        target = "app_news:news_single"   # ✅ اصلاح: app_news (نه app_news_en)
        redirect_slug = news.slug_en or news.slug
    else:
        target = "app_news:news_single"
        redirect_slug = news.slug

    return redirect(target, slug=redirect_slug, permanent=True)


# =====================================================
# NEWS TAG
# =====================================================
def news_tag(request, slug):
    """
    نمایش اخبار بر اساس تگ
    """
    is_english = is_english_request(request)

    # ✅ انتخاب اسلاگ درست بر اساس زبان + fallback
    if is_english:
        tag = (
            NewsTag.objects.filter(slug_en=slug).first()
            or NewsTag.objects.filter(slug=slug).first()
        )
    else:
        tag = NewsTag.objects.filter(slug=slug).first()

    if not tag:
        raise Http404(f"Tag '{slug}' not found")

    news_queryset = (
        News.objects
        .filter(status="published", tags=tag)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-publish_date_fa", "-id")
    )

    news_list = _paginate(request, news_queryset)

    context = {
        "tag": tag,
        "news_list": news_list,
        "active_category_slug": None,
        "categories_2": _get_categories_2(),   # ✅
        "seo": SEOManager.get_page("news"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("news_home.html", is_english),
        context,
    )


# =====================================================
# NEWS CATEGORY
# =====================================================
def news_category(request, slug):
    """
    نمایش اخبار بر اساس دسته‌بندی
    """
    is_english = is_english_request(request)

    # ✅ انتخاب اسلاگ درست بر اساس زبان + fallback به slug فارسی
    if is_english:
        category = (
            NewsCategory.objects.filter(slug_en=slug).first()
            or NewsCategory.objects.filter(slug=slug).first()
        )
    else:
        category = NewsCategory.objects.filter(slug=slug).first()

    if not category:
        raise Http404(f"Category '{slug}' not found")

    news_queryset = (
        News.objects
        .filter(status="published", category=category)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-publish_date_fa", "-id")
    )

    news_list = _paginate(request, news_queryset)

    context = {
        "category": category,
        "news_list": news_list,
        "active_category_slug": slug,
        "categories_2": _get_categories_2(),   # ✅ حالا در این view هم پاس داده می‌شود
        "seo": SEOManager.get_page("news"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("news_home.html", is_english),
        context,
    )


# =====================================================
# NEWS SEARCH
# =====================================================
def news_search(request):
    """
    جستجو در اخبار
    """
    is_english = is_english_request(request)

    query = request.GET.get("s", "").strip()

    news_queryset = (
        News.objects
        .filter(status="published")
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-publish_date_fa", "-id")
    )

    if query:
        news_queryset = news_queryset.filter(
            Q(title_fa__icontains=query) |
            Q(title_en__icontains=query) |
            Q(summary_fa__icontains=query) |
            Q(summary_en__icontains=query) |
            Q(content_fa__icontains=query) |
            Q(content_en__icontains=query) |
            Q(source__icontains=query) |
            Q(location__icontains=query)
        ).distinct()

    news_list = _paginate(request, news_queryset)

    context = {
        "news_list": news_list,
        "search_query": query,
        "active_category_slug": None,
        "categories_2": _get_categories_2(),   # ✅
        "seo": SEOManager.get_page("news"),
        "is_english": is_english,
    }

    return render(
        request,
        _get_template("news_home.html", is_english),
        context,
    )