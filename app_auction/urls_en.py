# app_auction/urls_en.py
from django.urls import path
from app_auction.views import (
    auction_home,
    auction_single,
    auction_tag,
    auction_search,
)

app_name = "app_auction_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/auction/ از urls.py اصلی میاد)
    # =====================================================

    path("", auction_home, name="auction_home_en"),
    path("category/<str:cat_name>/", auction_home, name="auction_category_en"),
    path("author/<str:author_username>/", auction_home, name="auction_author_en"),
    path("search/", auction_search, name="auction_search_en"),

    path("tag/<str:slug>/", auction_tag, name="auction_tag_en"),

    # ✅ URL جدید: /en/auction/auction-name/  (بدون pid)
    path("<str:slug>/", auction_single, name="auction_single_en"),
]