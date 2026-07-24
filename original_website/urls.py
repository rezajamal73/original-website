from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import render

# from app_core.sitemaps import StaticViewSitemap
# from app_blog.sitemaps import BlogSitemap
# from app_product.sitemaps import ProductSitemap
#
# sitemaps = {
#     "static": StaticViewSitemap,
#     "blog": BlogSitemap,
#     "app_product": ProductSitemap,
# }


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


handler404 = custom_404_view

urlpatterns = [
    path("", include("app_admin.urls")),

    path("", include("app_core.urls")),
    path("blog/", include("app_blog.urls")),
    path("news/", include("app_news.urls")),
    path("chart/", include("app_chart.urls")),
    path("product/", include("app_product.urls")),
    path("tender/", include("app_tender.urls")),
    path("tender_holding/", include("app_tender_holding.urls")),
    path("inquiry/", include("app_inquiry.urls")),
    path("auction/", include("app_auction.urls")),
    path("security_contact/", include("app_security.urls")),
    path("contact/", include("app_contact.urls")),
    path("reports/", include("app_reports.urls")),
    path("hr/", include("app_hr.urls")),
    path("media/", include("app_media.urls")),
    path("sale/", include("app_sale.urls")),
    path("catalog/", include("app_catalog.urls")),
    path("resume/", include("app_resume.urls")),
    path("", include("app_seo.urls")),

    # path(
    #     "sitemap.xml",
    #     sitemap,
    #     {"sitemaps": sitemaps},
    #     name="django.contrib.sitemaps.views.sitemap",
    # ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
