# original_website/urls.py
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import render


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


handler404 = custom_404_view


# =====================================================
# URLهای انگلیسی — زیر /en/
# =====================================================
english_urls = [
    # ============ Core & Products ============
    path("", include("app_core.urls_en")),
    path("product/", include("app_product.urls_en")),

    # ============ Content ============
    path("blog/", include("app_blog.urls_en")),
    path("news/", include("app_news.urls_en")),
    path("media/", include("app_media.urls_en")),

    # ============ Company ============
    path("chart/", include("app_chart.urls_en")),
    path("reports/", include("app_reports.urls_en")),
    path("catalog/", include("app_catalog.urls_en")),
    path("resume/", include("app_resume.urls_en")),

    # ============ Contact ============
    path("contact/", include("app_contact.urls_en")),
    path("security_contact/", include("app_security.urls_en")),

    # ============ Auction ============
    path("auction/", include("app_auction.urls_en")),

    # ============ Tender ============
    path("tender/", include("app_tender.urls_en")),
    path("tender_holding/", include("app_tender_holding.urls_en")),

    # ============ Inquiry ============
    path("inquiry/", include("app_inquiry.urls_en")),

    # ============ Sale ============
    path("sale/", include("app_sale.urls_en")),

    # ============ SEO ============
    # path("", include("app_seo.urls_en")),   # ← اگه urls_en داره، فعال کن
]


# =====================================================
# URLهای فارسی — بدون prefix
# =====================================================
persian_urls = [
    # ============ Admin ============
    path("", include("app_admin.urls")),

    # ============ Core ============
    path("", include("app_core.urls")),

    # ============ Content ============
    path("blog/", include("app_blog.urls")),
    path("news/", include("app_news.urls")),
    path("media/", include("app_media.urls")),

    # ============ Company ============
    path("chart/", include("app_chart.urls")),
    path("reports/", include("app_reports.urls")),
    path("catalog/", include("app_catalog.urls")),
    path("resume/", include("app_resume.urls")),
    path("hr/", include("app_hr.urls")),

    # ============ Contact ============
    path("contact/", include("app_contact.urls")),
    path("security_contact/", include("app_security.urls")),

    # ============ Products ============
    path("product/", include("app_product.urls")),

    # ============ Auction ============
    path("auction/", include("app_auction.urls")),

    # ============ Tender ============
    path("tender/", include("app_tender.urls")),
    path("tender_holding/", include("app_tender_holding.urls")),

    # ============ Inquiry ============
    path("inquiry/", include("app_inquiry.urls")),

    # ============ Sale ============
    path("sale/", include("app_sale.urls")),

    # ============ SEO ============
    path("", include("app_seo.urls")),
]


# =====================================================
# URL نهایی
# =====================================================
urlpatterns = [
    path("en/", include(english_urls)),   # ✅ انگلیسی اول
    path("", include(persian_urls)),       # ✅ فارسی دوم
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)