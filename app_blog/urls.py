from django.urls import path
from app_blog.views import *

app_name = "app_blog"

urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path("", blog_home, name="blog_home"),
    path("search_blog/", blog_search, name="search"),
    path("category/<str:slug>/", blog_home, name="blog_category"),
    path("author/<str:author_username>/", blog_home, name="blog_author"),
    path("tag/<str:slug>/", blog_tag, name="blog_tag"),

    # ✅ URL جدید با pid + slug
    path("<int:pid>/", blog_single_redirect, name="blog_single_old"),
    path("<int:pid>/<str:slug>/", blog_single, name="blog_single"),
]