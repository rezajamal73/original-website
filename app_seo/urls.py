from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import (
    StaticViewSitemap,
    ProductSitemap,
    BlogSitemap,
    NewsSitemap,
)


sitemaps = {

    "static": StaticViewSitemap,

    "products": ProductSitemap,

    "blogs": BlogSitemap,

    "news": NewsSitemap,

}


urlpatterns = [

    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": sitemaps
        },
        name="sitemap"
    ),

]