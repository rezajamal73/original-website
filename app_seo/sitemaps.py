# app_seo/sitemaps.py

"""
Sitemapهای app_seo — نسخه‌ی کامل و درست.

- همه‌ی اپ‌های پروژه پوشش داده شده.
- URL nameها دقیقاً بر اساس registry پروژه.
- فارسی و انگلیسی جداگانه.
- lastmod برای آبجکت‌ها.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse, NoReverseMatch
from django.conf import settings


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get_updated_at(obj):
    """خواندن امن آخرین تاریخ به‌روزرسانی."""
    for field in (
        "updated_at",
        "updated_at_fa",
        "updated_at_en",
        "created_at",
        "created_at_fa",
        "created_at_en",
        "publish_date",
        "publish_date_fa",
        "publish_date_en",
    ):
        value = getattr(obj, field, None)
        if value:
            return value
    return None


def _site_url():
    return getattr(settings, "SITE_URL", "").rstrip("/")


def _should_index(page_key):
    """چک می‌کنه آیا این صفحه اجازه‌ی ایندکس داره."""
    from .utils import SEOManager

    try:
        seo = SEOManager.get_page(page_key)
    except Exception:
        return True

    if seo is None:
        return True

    robots = getattr(seo, "robots", "") or ""

    if "noindex" in robots:
        return False

    if page_key in ("404", "search"):
        return False

    return True


def _safe_reverse(url_name, kwargs=None):
    """reverse امن. اگه خطا بده، None برمی‌گردونه."""
    try:
        return reverse(url_name, kwargs=kwargs or {})
    except NoReverseMatch:
        return None
    except Exception:
        return None


# =====================================================
#  Static Pages  —  صفحات ثابت فارسی
# =====================================================

class StaticViewSitemap(Sitemap):
    """
    صفحات ثابت + لیست‌های اصلی همه‌ی اپ‌ها (فارسی).
    """

    protocol = "https"
    priority = 0.8
    changefreq = "weekly"
    i18n = True

    # ---- صفحات ثابتی که به noindex احترام می‌ذارن ----
    SEO_PAGES = [
        ("home", "app_core:home"),
        ("about", "app_core:about"),
        ("contact", "app_core:contact"),
    ]

    # ---- لیست‌های اصلی اپ‌ها ----
    OTHER_URLS = [
        # app_core
        "app_core:category",

        # app_product
        "app_product:product_list",

        # app_blog
        "app_blog:blog_home",

        # app_news
        "app_news:news_home",

        # app_media
        "app_media:media_home",

        # app_resume
        "app_resume:resume",

        # app_catalog
        "app_catalog:catalog",

        # app_tender
        "app_tender:tender_home",

        # app_tender_holding
        "app_tender_holding:tender_holding_home",

        # app_auction
        "app_auction:auction_home",

        # app_hr
        "app_hr:hr_home",

        # app_chart
        "app_chart:chart",
        "app_chart:board_home",

        # app_inquiry
        "app_inquiry:inquiry_home",

        # app_reports
        "app_reports:vision_missions",
        "app_reports:financial",
        "app_reports:shareholder",
        "app_reports:governance",
        "app_reports:sustainability",
        "app_reports:certificate",
        "app_reports:department_contact_list",
        "app_reports:companies",

        # app_sale
        "app_sale:sales_chart",
    ]

    def items(self):
        valid = []

        # ---- SEO_PAGES با چک noindex ----
        for page_key, url_name in self.SEO_PAGES:
            if _safe_reverse(url_name) is None:
                continue
            if not _should_index(page_key):
                continue
            valid.append(url_name)

        # ---- OTHER_URLS ----
        seo_url_names = {u for _, u in self.SEO_PAGES}

        for url_name in self.OTHER_URLS:
            if url_name in seo_url_names:
                continue
            if _safe_reverse(url_name) is None:
                continue
            valid.append(url_name)

        return valid

    def location(self, item):
        return reverse(item)


# =====================================================
#  Static Pages EN  —  صفحات ثابت انگلیسی
# =====================================================

class StaticViewSitemapEN(Sitemap):
    """
    صفحات ثابت انگلیسی.
    """

    protocol = "https"
    priority = 0.8
    changefreq = "weekly"

    OTHER_URLS = [
        # app_core_en
        "app_core_en:home_en",
        "app_core_en:about_en",
        "app_core_en:contact_en",

        # app_product_en
        "app_product_en:product_list_en",

        # app_blog_en
        "app_blog_en:blog_home_en",

        # app_news_en
        "app_news_en:news_home_en",

        # app_media_en
        "app_media_en:media_home_en",

        # app_resume_en
        "app_resume_en:resume_en",

        # app_catalog_en
        "app_catalog_en:catalog_en",

        # app_tender_en
        "app_tender_en:tender_home_en",

        # app_tender_holding_en
        "app_tender_holding_en:tender_holding_home_en",

        # app_auction_en
        "app_auction_en:auction_home_en",

        # app_chart_en
        "app_chart_en:chart_en",
        "app_chart_en:board_home_en",

        # app_inquiry_en
        "app_inquiry_en:inquiry_home_en",

        # app_reports_en
        "app_reports_en:vision_missions_en",
        "app_reports_en:financial_en",
        "app_reports_en:shareholder_en",
        "app_reports_en:governance_en",
        "app_reports_en:sustainability_en",
        "app_reports_en:certificate_en",
        "app_reports_en:department_contact_list_en",
        "app_reports_en:companies_en",

        # app_sale_en
        "app_sale_en:sales_chart_en",
    ]

    def items(self):
        valid = []
        for url_name in self.OTHER_URLS:
            if _safe_reverse(url_name) is None:
                continue
            valid.append(url_name)
        return valid

    def location(self, item):
        return reverse(item)


# =====================================================
#  Products
# =====================================================

class ProductSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9
    i18n = True

    def items(self):
        try:
            from app_product.models import Product
            return Product.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return obj.get_absolute_url()
        except Exception:
            return ""


# =====================================================
#  Blogs
# =====================================================

class BlogSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    i18n = True

    def items(self):
        try:
            from app_blog.models import blog
            return blog.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_blog:blog_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  News
# =====================================================

class NewsSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.8
    i18n = True

    def items(self):
        try:
            from app_news.models import News
            return News.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_news:news_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  Media
# =====================================================

class MediaSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6
    i18n = True

    def items(self):
        try:
            from app_media.models import Media
            return Media.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_media:media_single",
                kwargs={"slug": obj.slug},
            )
        except Exception:
            return ""


# =====================================================
#  Tender
# =====================================================

class TenderSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    i18n = True

    def items(self):
        try:
            from app_tender.models import tender
            return tender.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_tender:tender_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  Tender Holding
# =====================================================

class HoldingSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    i18n = True

    def items(self):
        try:
            from app_tender_holding.models import holding
            return holding.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_tender_holding:tender_holding_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  Auction
# =====================================================

class AuctionSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    i18n = True

    def items(self):
        try:
            from app_auction.models import auction
            return auction.objects.filter(status="published")
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_auction:auction_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  Catalog
# =====================================================

class CatalogSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6
    i18n = True

    def items(self):
        try:
            from app_catalog.models import companycatalog
            return companycatalog.objects.all()
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return obj.get_absolute_url()
        except Exception:
            return ""


# =====================================================
#  HR / Job Opportunity
# =====================================================

class HRSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7
    i18n = True

    def items(self):
        try:
            from app_hr.models import jobopportunity
            return jobopportunity.objects.all()
        except Exception:
            return []

    def lastmod(self, obj):
        return _get_updated_at(obj)

    def location(self, obj):
        try:
            return reverse(
                "app_hr:hr_single",
                kwargs={"pid": obj.id},
            )
        except Exception:
            return ""


# =====================================================
#  Sitemap Index
# =====================================================

sitemaps = {
    "static": StaticViewSitemap,
    "static_en": StaticViewSitemapEN,
    "products": ProductSitemap,
    "blogs": BlogSitemap,
    "news": NewsSitemap,
    "media": MediaSitemap,
    "tenders": TenderSitemap,
    "holdings": HoldingSitemap,
    "auctions": AuctionSitemap,
    "catalogs": CatalogSitemap,
    "hr": HRSitemap,
}


