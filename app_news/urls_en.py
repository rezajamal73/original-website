# app_news/urls_en.py
from django.urls import path
from app_news.views import (
    news_home,
    news_single,
    news_single_redirect,
    news_tag,
    news_category,
    news_search,
)

app_name = "app_news_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/news/ از urls.py اصلی میاد)
    # =====================================================

    path("", news_home, name="news_home_en"),
    path("search/", news_search, name="news_search_en"),
    path("category/<str:slug>/", news_category, name="news_category_en"),
    path("tag/<str:slug>/", news_tag, name="news_tag_en"),
    path("<int:pid>/", news_single_redirect, name="news_single_old_en"),
    path("<int:pid>/<str:slug>/", news_single, name="news_single_en"),
]