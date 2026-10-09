# app_media/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from .models import Media
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core میاد
from app_core.url_helpers import is_english_request


# =====================================================
# PAGINATION HELPER
# =====================================================
def _paginate(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.get_page(page_number)
    except PageNotAnInteger:
        return paginator.get_page(1)
    except EmptyPage:
        return paginator.get_page(paginator.num_pages)


# =====================================================
# MEDIA HOME (LIST)
# =====================================================
def media_home(request, slug=None):
    """
    لیست رسانه‌ها (همه / بر اساس دسته)
    """
    is_english = is_english_request(request)

    media_queryset = (
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos")
        .order_by("order")
    )

    # ✅ فیلتر بر اساس slug (اگه دسته‌بندی داشتیم)
    # فعلاً Media مدل Category نداره، پس slug رو نادیده می‌گیریم
    # اگه بعداً MediaCategory اضافه شد، اینجا فیلتر کن

    media_sections = _paginate(request, media_queryset, per_page=6)

    template_name = (
        "LTR/media/media_home.html"
        if is_english
        else "RTL/media/media_home.html"
    )

    context = {
        "media_sections": media_sections,
        "active_slug": slug,
        "seo": SEOManager.get_page("media"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# MEDIA SINGLE — با pid + slug
# =====================================================
def media_single(request, pid, slug=None):
    """
    صفحه جزئیات یک رسانه
    """
    is_english = is_english_request(request)

    media = get_object_or_404(
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos"),
        pk=pid,
    )

    # ✅ اگه slug داده شده، بررسی کن
    if slug:
        correct_slug = media.slug_en if is_english else media.slug

        if correct_slug != slug:
            target = (
                "app_media_en:media_single_en"
                if is_english
                else "app_media:media_single"
            )
            return redirect(target, pid=pid, slug=correct_slug, permanent=True)

    template_name = (
        "LTR/media/media_single.html"
        if is_english
        else "RTL/media/media_single.html"
    )

    context = {
        "media": media,
        "images": media.images.all(),
        "videos": media.videos.all(),
        "seo": SEOManager.get_object(media),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# MEDIA SINGLE REDIRECT — از URL قدیمی /media/5/
# =====================================================
def media_single_redirect(request, pid):
    """
    ریدایرکت از URL قدیمی (فقط pid) به URL جدید (pid + slug).
    """
    is_english = is_english_request(request)

    media = get_object_or_404(Media, pk=pid)

    if is_english:
        target = "app_media_en:media_single_en"
        redirect_slug = media.slug_en or media.slug
    else:
        target = "app_media:media_single"
        redirect_slug = media.slug

    return redirect(target, pid=pid, slug=redirect_slug, permanent=True)


# =====================================================
# MEDIA SEARCH
# =====================================================
def media_search(request):
    """
    جستجو در رسانه‌ها
    """
    is_english = is_english_request(request)

    query = request.GET.get("s", "").strip()

    media_queryset = (
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos")
        .order_by("order")
    )

    if query:
        media_queryset = media_queryset.filter(
            Q(title_fa__icontains=query) |
            Q(title_en__icontains=query) |
            Q(summary_fa__icontains=query) |
            Q(summary_en__icontains=query)
        ).distinct()

    media_sections = _paginate(request, media_queryset, per_page=6)

    template_name = (
        "LTR/media/media_home.html"
        if is_english
        else "RTL/media/media_home.html"
    )

    context = {
        "media_sections": media_sections,
        "search_query": query,
        "seo": SEOManager.get_page("media"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# MEDIA TAG — فعلاً غیرفعال (چون MediaTag مدل نداریم)
# =====================================================
def media_tag(request, slug):
    """
    نمایش رسانه‌ها بر اساس تگ.

    ⚠️ توجه: مدل MediaTag توی app_media وجود نداره.
    این تابع فعلاً یه صفحه خالی نشون می‌ده.

    اگه بعداً MediaTag اضافه شد، این تابع رو کامل کن.
    """
    is_english = is_english_request(request)

    # ⚠️ چون MediaTag نداریم، یه صفحه خالی برمی‌گردونیم
    media_queryset = Media.objects.none()

    media_sections = _paginate(request, media_queryset, per_page=6)

    template_name = (
        "LTR/media/media_home.html"
        if is_english
        else "RTL/media/media_home.html"
    )

    context = {
        "tag_slug": slug,
        "media_sections": media_sections,
        "seo": SEOManager.get_page("media"),
        "is_english": is_english,
    }

    return render(request, template_name, context)