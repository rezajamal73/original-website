# app_seo/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings

from app_product.models import Product
from app_blog.models import blog
from app_news.models import News

from .utils import SEOManager


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get_updated_at(obj):
    """
    مدل‌ها فیلدهای متفاوتی دارند:
    - updated_at
    - updated_at_fa / updated_at_en
    - created_at_fa / created_at_en
    """
    for field in (
        "updated_at",
        "updated_at_fa",
        "updated_at_en",
        "created_at_fa",
        "created_at_en",
    ):
        value = getattr(obj, field, None)
        if value:
            return value
    return None


def _should_index(page_key):
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


# =====================================================
#  Static pages
# =====================================================

class StaticViewSitemap(Sitemap):

    protocol = "https"
    priority = 0.8
    changefreq = "weekly"
    i18n = True

    SEO_PAGES = [
        ("home", "app_core:home"),
        ("about", "app_core:about"),
        ("contact", "app_core:contact"),
    ]

    OTHER_URLS = [
        "app_product:product_list",
        "app_blog:blog_home",
        "app_news:news_home",
        "app_resume:resume",
        "app_media:home",
        "app_catalog:catalog",
    ]

    def items(self):
        valid = []

        for page_key, url_name in self.SEO_PAGES:
            try:
                reverse(url_name)
            except Exception:
                continue
            if not _should_index(page_key):
                continue
            valid.append(url_name)

        for url_name in self.OTHER_URLS:
            try:
                reverse(url_name)
            except Exception:
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
        return Product.objects.filter(status="published")

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
        return blog.objects.filter(status="published")

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
        return News.objects.filter(status="published")

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
#  Sitemap Index
# =====================================================

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "blogs": BlogSitemap,
    "news": NewsSitemap,
}