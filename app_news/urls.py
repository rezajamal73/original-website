# app_news/urls.py
from django.urls import path
from app_news.views import (
    news_home,
    news_single,
    news_tag,
    news_category,
    news_search,
)

app_name = "app_news"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /news/ از urls.py اصلی میاد)
    # =====================================================

    path("", news_home, name="news_home"),
    path("search/", news_search, name="news_search"),

    # ✅ slug → str (پشتیبانی از فارسی)
    path("category/<str:slug>/", news_category, name="news_category"),
    path("tag/<str:slug>/", news_tag, name="news_tag"),

    # ✅ URL جدید: /news/عنوان-خبر/  (بدون pid)
    path("<str:slug>/", news_single, name="news_single"),
]