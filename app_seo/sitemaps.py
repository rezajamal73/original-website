
# app_seo/sitemaps.py

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core.exceptions import FieldError
from django.db.models import Q
from django.urls import NoReverseMatch, reverse


# ============================================================
# URL helpers
# ============================================================

def safe_reverse(name):
    """
    Reverse a named URL safely.
    """
    try:
        return clean_path(reverse(name))
    except NoReverseMatch:
        return None


def updated_at(obj):
    """
    Return the latest available modification timestamp.
    """
    values = []

    for field in (
        "updated_at",
        "updated_at_fa",
        "updated_at_en",
        "modified_at",
        "created_at",
        "created_at_fa",
        "created_at_en",
    ):
        value = getattr(obj, field, None)

        if value is not None:
            values.append(value)

    if not values:
        return None

    try:
        return max(values)
    except (TypeError, ValueError):
        return values[0]


def _allowed_hosts():
    """
    Hosts accepted for absolute URLs.

    This intentionally does not trust arbitrary external URLs.
    """
    hosts = {
        "nkavosh.com",
        "www.nkavosh.com",
    }

    for host in getattr(settings, "ALLOWED_HOSTS", []):
        if not isinstance(host, str):
            continue

        host = host.strip().lower()

        if (
            host
            and host != "*"
            and not host.startswith(".")
        ):
            hosts.add(host)

    return hosts


def clean_path(value):
    """
    Normalize a local URL for use in a sitemap.

    - Accept local paths.
    - Accept absolute URLs only for allowed hosts.
    - Reject external hosts.
    - Remove query strings and fragments.
    - Reject protocol-relative URLs.
    - Reject malformed paths.
    """
    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    if any(ord(char) < 32 for char in value):
        return None

    if "\\" in value:
        return None

    if value.startswith("//"):
        return None

    try:
        parts = urlsplit(value)
    except ValueError:
        return None

    if parts.scheme or parts.netloc:
        if parts.scheme.lower() not in ("http", "https"):
            return None

        try:
            hostname = (parts.hostname or "").lower()
        except ValueError:
            return None

        if hostname not in _allowed_hosts():
            return None

        if parts.username or parts.password:
            return None

    path = parts.path

    if not path:
        return None

    if not path.startswith("/"):
        return None

    if path.startswith("//"):
        return None

    if "\\" in path:
        return None

    return path


def object_url(obj, english=False):
    """
    Get the language-specific URL of an object.
    """
    method_name = (
        "get_absolute_url_en"
        if english
        else "get_absolute_url"
    )

    method = getattr(obj, method_name, None)

    if not callable(method):
        return None

    try:
        return clean_path(method())
    except (
        NoReverseMatch,
        ValueError,
        AttributeError,
        TypeError,
    ):
        return None


# ============================================================
# Publication filters
# ============================================================

def published_objects(model, english=False):
    """
    Include published objects only.

    For models with a 'status' field, prefer the
    explicit 'published' status when supported.
    """
    qs = model.objects.all()

    fields = {
        field.name
        for field in model._meta.fields
    }

    if "status" in fields:
        status_field = model._meta.get_field("status")
        choices = getattr(status_field, "choices", None)

        if choices:
            valid_keys = set()

            for item in choices:
                try:
                    key, label = item
                except (TypeError, ValueError):
                    continue

                if isinstance(key, str):
                    valid_keys.add(key)

            if "published" in valid_keys:
                qs = qs.filter(status="published")
            else:
                excluded_statuses = (
                    "draft",
                    "deleted",
                    "hidden",
                    "inactive",
                    "archived",
                    "pending",
                    "rejected",
                )

                qs = qs.exclude(
                    status__in=excluded_statuses
                )
        else:
            qs = qs.exclude(
                status__in=(
                    "draft",
                    "deleted",
                    "hidden",
                    "inactive",
                    "archived",
                    "pending",
                    "rejected",
                )
            )

    if "is_active" in fields:
        qs = qs.filter(is_active=True)

    slug_field = (
        "slug_en"
        if english
        else "slug"
    )

    if slug_field in fields:
        qs = qs.exclude(
            **{slug_field: ""}
        ).exclude(
            **{f"{slug_field}__isnull": True}
        )

    return qs


# ============================================================
# Base sitemap
# ============================================================

class BaseSitemap(Sitemap):
    protocol = "https"
    i18n = False
    changefreq = "weekly"
    priority = 0.7

    def lastmod(self, obj):
        return updated_at(obj)


# ============================================================
# Static Persian pages
# ============================================================

class StaticViewSitemap(BaseSitemap):
    priority = 0.8

    URL_NAMES = [
        "app_core:home",
        "app_core:about",
        "app_core:contact",
        "app_core:category",
        "app_product:product_list",
        "app_blog:blog_home",
        "app_news:news_home",
        "app_media:media_home",
        "app_resume:resume",
        "app_catalog:catalog",
        "app_tender:tender_home",
        "app_tender_holding:tender_holding_home",
        "app_auction:auction_home",
        "app_hr:hr_home",
        "app_chart:chart",
        "app_chart:board_home",
        "app_inquiry:inquiry_home",
        "app_reports:vision_missions",
        "app_reports:financial",
        "app_reports:shareholder",
        "app_reports:governance",
        "app_reports:sustainability",
        "app_reports:certificate",
        "app_reports:department_contact_list",
        "app_reports:companies",
        "app_sale:sales_chart",
    ]

    def items(self):
        paths = []
        seen = set()

        for name in self.URL_NAMES:
            path = safe_reverse(name)

            if not path:
                continue

            if path in seen:
                continue

            seen.add(path)
            paths.append(path)

        return paths

    def location(self, item):
        return item


# ============================================================
# Static English pages
# ============================================================

class StaticViewSitemapEN(BaseSitemap):
    priority = 0.8

    URL_NAMES = [
        "app_core_en:home_en",
        "app_core_en:about_en",
        "app_core_en:contact_en",
        "app_product_en:product_list_en",
        "app_blog_en:blog_home_en",
        "app_news_en:news_home_en",
        "app_media_en:media_home_en",
        "app_resume_en:resume_en",
        "app_catalog_en:catalog_en",
        "app_tender_en:tender_home_en",
        "app_tender_holding_en:tender_holding_home_en",
        "app_auction_en:auction_home_en",
        "app_chart_en:chart_en",
        "app_chart_en:board_home_en",
        "app_inquiry_en:inquiry_home_en",
        "app_reports_en:vision_missions_en",
        "app_reports_en:financial_en",
        "app_reports_en:shareholder_en",
        "app_reports_en:governance_en",
        "app_reports_en:sustainability_en",
        "app_reports_en:certificate_en",
        "app_reports_en:department_contact_list_en",
        "app_reports_en:companies_en",
        "app_sale_en:sales_chart_en",
    ]

    def items(self):
        paths = []
        seen = set()

        for name in self.URL_NAMES:
            path = safe_reverse(name)

            if not path:
                continue

            if path in seen:
                continue

            seen.add(path)
            paths.append(path)

        return paths

    def location(self, item):
        return item


# ============================================================
# Dynamic sitemap base
# ============================================================

class DynamicSitemap(BaseSitemap):
    model = None
    english = False
    priority = 0.7

    def items(self):
        if self.model is None:
            return []

        candidates = published_objects(
            self.model,
            english=self.english,
        )

        valid = []
        seen = set()

        for obj in candidates.iterator():
            path = object_url(
                obj,
                english=self.english,
            )

            if not path:
                continue

            if path == "/":
                continue

            if path in seen:
                continue

            seen.add(path)
            valid.append(obj)

        return valid

    def location(self, obj):
        path = object_url(
            obj,
            english=self.english,
        )

        if not path or path == "/":
            raise ValueError(
                "Invalid sitemap URL for object "
                + str(obj.pk)
            )

        return path


# ============================================================
# Products
# ============================================================

from app_product.models import Product


class ProductSitemap(DynamicSitemap):
    model = Product
    priority = 0.9


class ProductEnglishSitemap(DynamicSitemap):
    model = Product
    english = True
    priority = 0.9


# ============================================================
# Blog
# ============================================================

from app_blog.models import blog


class BlogSitemap(DynamicSitemap):
    model = blog


class BlogEnglishSitemap(DynamicSitemap):
    model = blog
    english = True


# ============================================================
# News
# ============================================================

from app_news.models import News


class NewsSitemap(DynamicSitemap):
    model = News
    changefreq = "daily"
    priority = 0.8


class NewsEnglishSitemap(DynamicSitemap):
    model = News
    english = True
    changefreq = "daily"
    priority = 0.8


# ============================================================
# Media
# ============================================================

from app_media.models import Media


class MediaSitemap(DynamicSitemap):
    model = Media
    priority = 0.6


class MediaEnglishSitemap(DynamicSitemap):
    model = Media
    english = True
    priority = 0.6


# ============================================================
# Tenders
# ============================================================

from app_tender.models import Tender


class TenderSitemap(DynamicSitemap):
    model = Tender


class TenderEnglishSitemap(DynamicSitemap):
    model = Tender
    english = True


# ============================================================
# Tender Holding
# ============================================================

from app_tender_holding.models import Holding


class HoldingSitemap(DynamicSitemap):
    model = Holding


class HoldingEnglishSitemap(DynamicSitemap):
    model = Holding
    english = True


# ============================================================
# Auctions
# ============================================================

from app_auction.models import Auction


class AuctionSitemap(DynamicSitemap):
    model = Auction


class AuctionEnglishSitemap(DynamicSitemap):
    model = Auction
    english = True


# ============================================================
# Sitemap registry
# ============================================================

sitemaps = {
    "static": StaticViewSitemap,
    "static_en": StaticViewSitemapEN,

    "products": ProductSitemap,
    "products_en": ProductEnglishSitemap,

    "blogs": BlogSitemap,
    "blogs_en": BlogEnglishSitemap,

    "news": NewsSitemap,
    "news_en": NewsEnglishSitemap,

    "media": MediaSitemap,
    "media_en": MediaEnglishSitemap,

    "tenders": TenderSitemap,
    "tenders_en": TenderEnglishSitemap,

    "holdings": HoldingSitemap,
    "holdings_en": HoldingEnglishSitemap,

    "auctions": AuctionSitemap,
    "auctions_en": AuctionEnglishSitemap,
}
