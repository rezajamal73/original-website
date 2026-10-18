
# app_seo/urls.py

from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import sitemaps
from .views import robots_txt, sitemap_view


urlpatterns = [
    # XML sitemap for search engines
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),

    # Human-readable sitemap
    path(
        "map/",
        sitemap_view,
        name="sitemap_view",
    ),

    # Robots.txt
    path(
        "robots.txt",
        robots_txt,
        name="robots_txt",
    ),
]
