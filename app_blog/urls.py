# app_blog/urls.py

from django.urls import path
from app_blog.views import *

app_name = "app_blog"


urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path(
        "",
        blog_home,
        name="blog_home"
    ),

    path(
        "search_blog/",
        blog_search,
        name="search"
    ),

    path(
        "category/<slug:slug>/",
        blog_home,
        name="blog_category"
    ),

    path(
        "author/<str:author_username>/",
        blog_home,
        name="blog_author"
    ),

    path(
        "tag/<slug:slug>/",
        blog_tag,
        name="blog_tag"
    ),

    path(
        "<int:pid>/",
        blog_single,
        name="blog_single"
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    path(
        "en/",
        blog_home,
        name="blog_home_en"
    ),

    path(
        "en/search_blog/",
        blog_search,
        name="search_en"
    ),

    path(
        "en/category/<slug:slug>/",
        blog_home,
        name="blog_category_en"
    ),

    path(
        "en/author/<str:author_username>/",
        blog_home,
        name="blog_author_en"
    ),

    path(
        "en/tag/<slug:slug>/",
        blog_tag,
        name="blog_tag_en"
    ),

    path(
        "en/<int:pid>/",
        blog_single,
        name="blog_single_en"
    ),

]