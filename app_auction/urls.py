# app_auction/urls.py
from django.urls import path
from app_auction.views import (
    auction_home,
    auction_single,
    auction_tag,
    auction_search,
)

app_name = "app_auction"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /auction/ از urls.py اصلی میاد)
    # =====================================================

    path("", auction_home, name="auction_home"),
    path("category/<str:cat_name>/", auction_home, name="auction_category"),
    path("author/<str:author_username>/", auction_home, name="auction_author"),
    path("search/", auction_search, name="auction_search"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("tag/<str:slug>/", auction_tag, name="auction_tag"),

    # ✅ URL جدید: /auction/نام-مزایده/  (بدون pid)
    path("<str:slug>/", auction_single, name="auction_single"),
]