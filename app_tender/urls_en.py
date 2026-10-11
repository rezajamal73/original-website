# app_tender/urls_en.py
from django.urls import path
from app_tender.views import (
    tender_home,
    tender_search,
    tender_tag,
    tender_single,
)

app_name = "app_tender_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/tender/ از urls.py اصلی میاد)
    # =====================================================

    path("", tender_home, name="tender_home_en"),
    path("search/", tender_search, name="search_en"),
    path("category/<str:cat_name>/", tender_home, name="tender_category_en"),
    path("tag/<str:slug>/", tender_tag, name="tender_tag_en"),

    # ✅ URL جدید: /en/tender/tender-name/  (بدون pid)
    path("<str:slug>/", tender_single, name="tender_single_en"),
]