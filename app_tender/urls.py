# app_tender/urls.py
from django.urls import path
from app_tender.views import (
    tender_home,
    tender_search,
    tender_tag,
    tender_single,
)

app_name = "app_tender"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /tender/ از urls.py اصلی میاد)
    # =====================================================

    path("", tender_home, name="tender_home"),
    path("search/", tender_search, name="search"),
    path("category/<str:cat_name>/", tender_home, name="tender_category"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("tag/<str:slug>/", tender_tag, name="tender_tag"),

    # ✅ URL جدید: /tender/نام-مناقصه/  (بدون pid)
    path("<str:slug>/", tender_single, name="tender_single"),
]