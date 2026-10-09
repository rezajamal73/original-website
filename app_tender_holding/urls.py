from django.urls import path
from app_tender_holding.views import *

app_name = "app_tender_holding"

urlpatterns = [
    # =====================================================
    # PERSIAN
    # =====================================================

    path("", tender_holding_home, name="tender_holding_home"),
    path("search/", tender_holding_search, name="search"),
    path("category/<str:cat_name>/", tender_holding_home, name="tender_holding_category"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("tag/<str:slug>/", tender_holding_tag, name="tender_holding_tag"),

    # ✅ Redirect از URL قدیمی
    path("<int:pid>/", tender_holding_single_redirect, name="tender_holding_single_old"),

    # ✅ URL جدید با pid + slug
    path("<int:pid>/<str:slug>/", tender_holding_single, name="tender_holding_single"),
]