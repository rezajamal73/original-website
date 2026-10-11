# app_tender_holding/urls_en.py
from django.urls import path
from app_tender_holding.views import (
    tender_holding_home,
    tender_holding_search,
    tender_holding_tag,
    tender_holding_single,
)

app_name = "app_tender_holding_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/tender_holding/ از urls.py اصلی میاد)
    # =====================================================

    path("", tender_holding_home, name="tender_holding_home_en"),
    path("search/", tender_holding_search, name="search_en"),
    path("category/<str:cat_name>/", tender_holding_home, name="tender_holding_category_en"),
    path("tag/<str:slug>/", tender_holding_tag, name="tender_holding_tag_en"),

    # ✅ URL جدید: /en/tender_holding/holding-name/  (بدون pid)
    path("<str:slug>/", tender_holding_single, name="tender_holding_single_en"),
]