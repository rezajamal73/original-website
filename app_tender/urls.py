from django.urls import path
from app_tender.views import *

app_name = "app_tender"

urlpatterns = [
    # =====================================================
    # PERSIAN
    # =====================================================

    path("", tender_home, name="tender_home"),
    path("search/", tender_search, name="search"),
    path("category/<str:cat_name>/", tender_home, name="tender_category"),

    # ✅ slug → str (برای پشتیبانی از فارسی)
    path("tag/<str:slug>/", tender_tag, name="tender_tag"),

    # ✅ URL جدید با pid + slug (برای دوزبانه کامل)
    path("<int:pid>/", tender_single_redirect, name="tender_single_old"),
    path("<int:pid>/<str:slug>/", tender_single, name="tender_single"),
]