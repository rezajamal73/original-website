# app_seo/urls.py

from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import sitemaps
from .views import robots_txt


urlpatterns = [

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),

    path(
        "robots.txt",
        robots_txt,
        name="robots_txt",
    ),

]