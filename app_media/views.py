# app/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Media
from app_seo.utils import SEOManager


# ------------------------------------------------------
#   MEDIA HOME (LIST)
# ------------------------------------------------------

def media_home(request):

    media_queryset = (
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos")
        .order_by("order")
    )

    paginator = Paginator(media_queryset, 6)

    media_sections = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "media_sections": media_sections,
        "seo": SEOManager.get_page("media"),
    }

    return render(
        request,
        "RTL/media/media_home.html",
        context,
    )


# ------------------------------------------------------
#   MEDIA SINGLE
# ------------------------------------------------------

def media_single(request, pk):

    media = get_object_or_404(
        Media.objects
        .filter(status="published")
        .prefetch_related("images", "videos"),
        pk=pk,
    )

    context = {
        "media": media,
        "images": media.images.all(),
        "videos": media.videos.all(),
        "seo": SEOManager.get_object(media),
    }

    return render(
        request,
        "RTL/media/media_single.html",
        context,
    )