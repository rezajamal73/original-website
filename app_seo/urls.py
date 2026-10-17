# app_seo/urls.py

from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import sitemaps
from .views import robots_txt, sitemap_view


urlpatterns = [

    # ==========================================
    # Original XML Sitemap - Google
    # ==========================================

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),

    # ==========================================
    # Human-readable Sitemap
    # ==========================================

    path(
      "map/",
      sitemap_view,
       name="sitemap_view",
    ),

    # ==========================================
    # Robots.txt
    # ==========================================

    path(
        "robots.txt",
        robots_txt,
        name="robots_txt",
    ),

]