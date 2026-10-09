# app_news/urls.py
from django.urls import path
from app_news.views import (
    news_home,
    news_single,
    news_single_redirect,
    news_tag,
    news_category,
    news_search,
)

app_name = "app_news"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /news/ از urls.py اصلی میاد)
    # =====================================================

    # صفحه اصلی اخبار
    path("", news_home, name="news_home"),

    # جستجو
    path("search/", news_search, name="news_search"),

    # فیلتر دسته‌بندی — ✅ slug → str (پشتیبانی از فارسی)
    path("category/<str:slug>/", news_category, name="news_category"),

    # فیلتر تگ — ✅ slug → str
    path("tag/<str:slug>/", news_tag, name="news_tag"),

    # ✅ Redirect از URL قدیمی /news/5/
    path("<int:pid>/", news_single_redirect, name="news_single_old"),

    # ✅ URL جدید: /news/5/عنوان-خبر/
    path("<int:pid>/<str:slug>/", news_single, name="news_single"),
]