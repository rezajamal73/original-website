from django.urls import path
from app_blog.views import *

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

    # ✅ URL جدید با pid + slug
    path("<int:pid>/", blog_single_redirect, name="blog_single_old_en"),
    path("<int:pid>/<str:slug>/", blog_single, name="blog_single_en"),
]