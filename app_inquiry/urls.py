# app_inquiry/urls.py
from django.urls import path
from .views import (
    inquiry_home,
    inquiry_single,
    inquiry_tag,
    inquiry_search,
)

app_name = "app_inquiry"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /inquiry/ از urls.py اصلی میاد)
    # =====================================================

    path("", inquiry_home, name="inquiry_home"),
    path("search/", inquiry_search, name="search"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("category/<str:slug>/", inquiry_home, name="inquiry_category"),
    path("tag/<str:slug>/", inquiry_tag, name="inquiry_tag"),

    # ✅ URL جدید: /inquiry/نام-استعلام/  (بدون pid)
    path("<str:slug>/", inquiry_single, name="inquiry_single"),
]