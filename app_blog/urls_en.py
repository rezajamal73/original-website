# app_blog/urls_en.py
from django.urls import path
from app_blog.views import (
    blog_home,
    blog_search,
    blog_tag,
    blog_single,
)

app_name = "app_blog_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/blog/ از urls.py اصلی میاد)
    # =====================================================

    path("", blog_home, name="blog_home_en"),
    path("search_blog/", blog_search, name="search_en"),
    path("category/<str:slug>/", blog_home, name="blog_category_en"),
    path("author/<str:author_username>/", blog_home, name="blog_author_en"),
    path("tag/<str:slug>/", blog_tag, name="blog_tag_en"),

    # ✅ URL جدید: /en/blog/post-name/  (بدون pid)
    path("<str:slug>/", blog_single, name="blog_single_en"),
]