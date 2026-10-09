# app_inquiry/urls.py
from django.urls import path
from .views import (
    inquiry_home,
    inquiry_single,
    inquiry_single_redirect,
    inquiry_tag,
    inquiry_search,
)

app_name = "app_inquiry"

urlpatterns = [
    # =====================================================
    # PERSIAN
    # =====================================================

    path("", inquiry_home, name="inquiry_home"),
    path("search/", inquiry_search, name="search"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("category/<str:slug>/", inquiry_home, name="inquiry_category"),

    # ✅ slug → str
    path("tag/<str:slug>/", inquiry_tag, name="inquiry_tag"),

    # ✅ Redirect از URL قدیمی
    path("<int:pid>/", inquiry_single_redirect, name="inquiry_single_old"),

    # ✅ URL جدید با pid + slug
    path("<int:pid>/<str:slug>/", inquiry_single, name="inquiry_single"),
]