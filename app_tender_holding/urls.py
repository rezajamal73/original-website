# app_tender_holding/urls.py
from django.urls import path
from app_tender_holding.views import (
    tender_holding_home,
    tender_holding_search,
    tender_holding_tag,
    tender_holding_single,
)

app_name = "app_tender_holding"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /tender_holding/ از urls.py اصلی میاد)
    # =====================================================

    path("", tender_holding_home, name="tender_holding_home"),
    path("search/", tender_holding_search, name="search"),
    path("category/<str:cat_name>/", tender_holding_home, name="tender_holding_category"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("tag/<str:slug>/", tender_holding_tag, name="tender_holding_tag"),

    # ✅ URL جدید: /tender_holding/نام-هلدینگ/  (بدون pid)
    path("<str:slug>/", tender_holding_single, name="tender_holding_single"),
]