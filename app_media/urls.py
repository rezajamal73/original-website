# app_media/urls.py
from django.urls import path
from app_media import views

app_name = "app_media"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /media/ از urls.py اصلی میاد)
    # =====================================================

    # Media Home
    path(
        "",
        views.media_home,
        name="media_home",
    ),

    # Media Search
    path(
        "search/",
        views.media_search,
        name="media_search",
    ),

    # Media Category
    path(
        "category/<str:slug>/",
        views.media_home,
        name="media_category",
    ),

    # Media Tag
    path(
        "tag/<str:slug>/",
        views.media_tag,
        name="media_tag",
    ),

    # ✅ URL جدید: /media/عنوان/  (بدون pid)
    path(
        "<str:slug>/",
        views.media_single,
        name="media_single",
    ),
]