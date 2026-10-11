# app_blog/urls.py
from django.urls import path
from app_blog.views import (
    blog_home,
    blog_search,
    blog_tag,
    blog_single,
)

app_name = "app_blog"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /blog/ از urls.py اصلی میاد)
    # =====================================================

    path("", blog_home, name="blog_home"),
    path("search_blog/", blog_search, name="search"),
    path("category/<str:slug>/", blog_home, name="blog_category"),
    path("author/<str:author_username>/", blog_home, name="blog_author"),
    path("tag/<str:slug>/", blog_tag, name="blog_tag"),

    # ✅ URL جدید: /blog/نام-مقاله/  (بدون pid)
    path("<str:slug>/", blog_single, name="blog_single"),
]