from django.urls import path, include
from app_blog.views import *
app_name = 'app_blog'

urlpatterns = [
    path("", blog_home, name="blog_home"),
    path("search_blog/", blog_search, name="search"),
    path("category/<str:cat_name>/", blog_home, name="blog_category"),
    path("author/<str:author_username>/", blog_home, name="blog_author"),
    path("tag/<slug:slug>/", blog_tag, name="blog_tag"),
    path("<int:pid>/", blog_single, name="blog_single"),
]