
# app_media/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Media
from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English pages based on URL name.

    Persian:
        home
        single

    English:
        home_en
        single_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


# =====================================================
# MEDIA HOME (LIST)
# =====================================================

def media_home(request):

    is_english = is_english_request(request)

    media_queryset = (
        Media.objects
        .filter(status="published")
        .prefetch_related(
            "images",
            "videos"
        )
        .order_by("order")
    )

    paginator = Paginator(
        media_queryset,
        6
    )

    media_sections = paginator.get_page(
        request.GET.get("page")
    )

    template_name = (
        "LTR/media/media_home.html"
        if is_english
        else "RTL/media/media_home.html"
    )

    context = {
        "media_sections": media_sections,
        "seo": SEOManager.get_page("media"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context,
    )


# =====================================================
# MEDIA SINGLE
# =====================================================

def media_single(request, pk):

    is_english = is_english_request(request)

    media = get_object_or_404(
        Media.objects
        .filter(
            status="published"
        )
        .prefetch_related(
            "images",
            "videos"
        ),
        pk=pk,
    )

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

    return render(
        request,
        template_name,
        context,
    )

