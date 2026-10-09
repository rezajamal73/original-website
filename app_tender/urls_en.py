from django.urls import path
from app_tender.views import *

app_name = "app_tender_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/tender/ از urls.py اصلی میاد)
    # =====================================================

    path("", tender_home, name="tender_home_en"),
    path("search/", tender_search, name="search_en"),
    path("category/<str:cat_name>/", tender_home, name="tender_category_en"),
    path("tag/<str:slug>/", tender_tag, name="tender_tag_en"),

    # ✅ URL جدید با pid + slug
    path("<int:pid>/", tender_single_redirect, name="tender_single_old_en"),
    path("<int:pid>/<str:slug>/", tender_single, name="tender_single_en"),
]