# app_inquiry/urls_en.py
from django.urls import path
from .views import (
    inquiry_home,
    inquiry_single,
    inquiry_tag,
    inquiry_search,
)

app_name = "app_inquiry_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/inquiry/ از urls.py اصلی میاد)
    # =====================================================

    path("", inquiry_home, name="inquiry_home_en"),
    path("search/", inquiry_search, name="search_en"),
    path("category/<str:slug>/", inquiry_home, name="inquiry_category_en"),
    path("tag/<str:slug>/", inquiry_tag, name="inquiry_tag_en"),

    # ✅ URL جدید: /en/inquiry/inquiry-name/  (بدون pid)
    path("<str:slug>/", inquiry_single, name="inquiry_single_en"),
]