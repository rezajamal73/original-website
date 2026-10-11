# app_media/urls_en.py
from django.urls import path
from app_media import views

app_name = "app_media_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/media/ از urls.py اصلی میاد)
    # =====================================================

    path(
        "",
        views.media_home,
        name="media_home_en",
    ),

    path(
        "search/",
        views.media_search,
        name="media_search_en",
    ),

    path(
        "category/<str:slug>/",
        views.media_home,
        name="media_category_en",
    ),

    path(
        "tag/<str:slug>/",
        views.media_tag,
        name="media_tag_en",
    ),

    # ✅ URL جدید: /en/media/media-title/  (بدون pid)
    path(
        "<str:slug>/",
        views.media_single,
        name="media_single_en",
    ),
]