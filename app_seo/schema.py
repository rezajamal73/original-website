
# app_seo/schema.py

import json
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from django.conf import settings


# =====================================================
# General helpers
# =====================================================

def _get(obj, *names, default=None):
    if obj is None:
        return default

    for name in names:
        try:
            value = getattr(obj, name, None)
        except (AttributeError, ValueError):
            continue

        if value is not None and value != "":
            return value

    return default


def _site_origin():
    configured = str(
        getattr(settings, "SITE_URL", "") or ""
    ).strip()

    try:
        parts = urlsplit(configured)
        if (
            parts.scheme == "https"
            and parts.hostname in {
                "nkavosh.com",
                "www.nkavosh.com",
            }
            and not parts.username
            and not parts.password
        ):
            return "https://" + parts.netloc
    except ValueError:
        pass

    return "https://nkavosh.com"


def _absolute_url(value, allow_external=False):
    if not value:
        return ""

    value = str(value).strip()

    if (
        not value
        or value.startswith("//")
        or "\\" in value
        or any(ord(char) < 32 for char in value)
    ):
        return ""

    try:
        parts = urlsplit(value)
    except ValueError:
        return ""

    if parts.scheme or parts.netloc:
        if parts.scheme not in ("http", "https"):
            return ""

        if not parts.hostname:
            return ""

        if parts.username or parts.password:
            return ""

        if not allow_external and parts.hostname.lower() not in {
            "nkavosh.com",
            "www.nkavosh.com",
        }:
            return ""

        return value

    if value.startswith("/"):
        return _site_origin() + value

    return _site_origin() + "/" + value


def _site_name():
    return (
        getattr(settings, "SITE_NAME", None)
        or "پارسا نوین کاوش"
    )


def _site_logo():
    return getattr(settings, "SITE_LOGO_URL", "") or ""


def _social_links():
    links = getattr(settings, "SITE_SOCIAL_LINKS", [])

    if not isinstance(links, (list, tuple)):
        return []

    result = []

    for link in links:
        url = _absolute_url(
            link,
            allow_external=True,
        )
        if url:
            result.append(url)

    return result


def _site_language(seo=None):
    if seo is not None and getattr(
        seo, "is_english", False
    ):
        return "en"

    language = _get(seo, "language")

    if language:
        return str(language)

    return getattr(
        settings,
        "LANGUAGE_CODE",
        "fa",
    )


def _image_url(obj, *names):
    if obj is None:
        return ""

    for name in names:
        image = getattr(obj, name, None)

        if not image:
            continue

        try:
            raw_url = image.url
        except (AttributeError, ValueError, OSError):
            continue

        url = _absolute_url(raw_url)

        if url:
            return url

    return ""


def _iso_date(value):
    if value is None:
        return ""

    try:
        return value.isoformat()
    except (AttributeError, TypeError, ValueError):
        return ""


def _object_url(seo, obj=None):
    url = _get(seo, "canonical", "url")

    if url:
        valid_url = _absolute_url(url)
        if valid_url:
            return valid_url

    if obj is None:
        return ""

    english = bool(
        getattr(seo, "is_english", False)
    )

    method_name = (
        "get_absolute_url_en"
        if english
        else "get_absolute_url"
    )

    method = getattr(obj, method_name, None)

    if not callable(method):
        return ""

    try:
        return _absolute_url(method())
    except (
        AttributeError,
        ValueError,
        TypeError,
    ):
        return ""


def _valid_price(value):
    if value is None or value == "":
        return None

    try:
        number = Decimal(str(value))

        if not number.is_finite():
            return None

        if number <= 0:
            return None

        return number

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return None


# =====================================================
# BreadcrumbList
# =====================================================

def _build_breadcrumb_schema(breadcrumb_items):
    if not isinstance(
        breadcrumb_items,
        (list, tuple),
    ):
        return None

    elements = []

    for item in breadcrumb_items:
        if isinstance(item, dict):
            label = item.get("label")
            raw_url = item.get("url")
        else:
            label = getattr(item, "label", None)
            raw_url = getattr(item, "url", None)

        url = _absolute_url(raw_url)

        if not url:
            continue

        name = str(label or "").strip() or url

        elements.append({
            "@type": "ListItem",
            "position": len(elements) + 1,
            "name": name,
            "item": url,
        })

    if len(elements) < 2:
        return None

    return {
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


# =====================================================
# Organization and WebSite
# =====================================================

def _build_organization():
    organization = {
        "@type": "Organization",
        "name": _site_name(),
        "url": _site_origin() + "/",
    }

    logo = _absolute_url(_site_logo())

    if logo:
        organization["logo"] = logo

    socials = _social_links()

    if socials:
        organization["sameAs"] = socials

    return organization


def _build_website():
    return {
        "@type": "WebSite",
        "name": _site_name(),
        "url": _site_origin() + "/",
    }


def _build_home_graph(seo=None):
    graph = [
        _build_organization(),
        _build_website(),
    ]

    if seo is not None:
        graph.append(
            _build_web_page(
                seo,
                schema_type="WebPage",
            )
        )

    return {
        "@context": "https://schema.org",
        "@graph": graph,
    }


# =====================================================
# WebPage
# =====================================================

def _build_web_page(seo, schema_type="WebPage"):
    page = {
        "@type": schema_type,
        "name": (
            _get(seo, "title")
            or _site_name()
        ),
        "description": (
            _get(seo, "description")
            or ""
        ),
    }

    url = _object_url(seo)

    if url:
        page["url"] = url

    language = (
        _get(seo, "language")
        or _site_language(seo)
    )

    if language:
        page["inLanguage"] = language

    return page


# =====================================================
# Product
# =====================================================

def _build_product(seo, obj):
    product = {
        "@type": "Product",
        "name": (
            _get(seo, "title")
            or _get(
                obj,
                "title_fa",
                "title_en",
                "title",
            )
            or ""
        ),
    }

    description = (
        _get(seo, "description")
        or _get(
            obj,
            "description_fa",
            "description_en",
            "description",
            "summary_fa",
        )
    )

    if description:
        product["description"] = str(description)

    url = _object_url(seo, obj)

    if url:
        product["url"] = url

    image = _image_url(
        obj,
        "main_image",
        "image",
        "cover",
    )

    if image:
        product["image"] = image

    brand = _get(
        obj,
        "brand",
        "brand_name",
    )

    if brand:
        product["brand"] = {
            "@type": "Brand",
            "name": str(brand),
        }

    sku = _get(
        obj,
        "sku",
        "code",
    )

    if sku:
        product["sku"] = str(sku)

    price = _get(
        obj,
        "price",
        "final_price",
        "sale_price",
    )

    valid_price = _valid_price(price)

    currency = (
        _get(obj, "currency")
        or "IRR"
    )

    if valid_price is not None and url:
        product["offers"] = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": str(currency),
            "price": str(valid_price),
        }

    return product


# =====================================================
# Article and NewsArticle
# =====================================================

def _build_article(
    seo,
    obj,
    schema_type="Article",
):
    article = {
        "@type": schema_type,
        "headline": (
            _get(seo, "title")
            or _get(
                obj,
                "title_fa",
                "title_en",
                "title",
            )
            or ""
        ),
        "description": (
            _get(seo, "description")
            or _get(
                obj,
                "description_fa",
                "description_en",
                "description",
            )
            or ""
        ),
    }

    url = _object_url(seo, obj)

    if url:
        article["url"] = url
        article["mainEntityOfPage"] = {
            "@type": "WebPage",
            "@id": url,
        }

    image = _image_url(
        obj,
        "image",
        "cover",
        "thumbnail",
    )

    if image:
        article["image"] = image

    published = _get(
        obj,
        "publish_date",
        "publish_date_fa",
        "publish_date_en",
        "created_at",
        "created_at_fa",
    )

    published_date = _iso_date(published)

    if published_date:
        article["datePublished"] = published_date

    updated = _get(
        obj,
        "updated_at",
        "updated_at_fa",
    )

    modified_date = _iso_date(updated)

    if modified_date:
        article["dateModified"] = modified_date

    author = _get(obj, "author")

    if author:
        article["author"] = {
            "@type": "Person",
            "name": str(author),
        }
    else:
        article["author"] = {
            "@type": "Organization",
            "name": _site_name(),
        }

    article["inLanguage"] = _site_language(seo)

    return article


# =====================================================
# Person and Resume
# =====================================================

def _build_person(seo, obj):
    person = {
        "@type": "Person",
        "name": (
            _get(seo, "title")
            or _get(obj, "full_name", "name")
            or ""
        ),
    }

    job_title = _get(
        obj,
        "job_title",
        "position",
    )

    if job_title:
        person["jobTitle"] = str(job_title)

    email = _get(obj, "email")

    if email:
        person["email"] = str(email)

    phone = _get(obj, "phone")

    if phone:
        person["telephone"] = str(phone)

    return person


# =====================================================
# VideoObject
# =====================================================

def _build_video(seo, obj):
    video = {
        "@type": "VideoObject",
        "name": (
            _get(seo, "title")
            or _get(obj, "title_fa", "title_en", "title")
            or ""
        ),
        "description": (
            _get(seo, "description")
            or ""
        ),
    }

    url = _object_url(seo, obj)

    if url:
        video["url"] = url

    thumbnail = _image_url(
        obj,
        "thumbnail",
        "image",
        "cover",
    )

    if thumbnail:
        video["thumbnailUrl"] = thumbnail

    published = _get(
        obj,
        "publish_date",
        "publish_date_fa",
        "created_at",
        "created_at_fa",
    )

    published_date = _iso_date(published)

    if published_date:
        video["uploadDate"] = published_date

    content_url = _image_url(
        obj,
        "video",
        "file",
    )

    if content_url:
        video["contentUrl"] = content_url

    return video


# =====================================================
# Schema type selection
# =====================================================

def _resolve_schema_type(seo):
    explicit = _get(seo, "schema_type")

    if explicit and explicit != "auto":
        return str(explicit)

    content_type = (
        _get(seo, "content_type")
        or "page"
    )

    page_key = (
        _get(seo, "page_key")
        or ""
    )

    if content_type == "page":
        if page_key == "about":
            return "AboutPage"

        if page_key in (
            "contact",
            "contact_security",
        ):
            return "ContactPage"

        if page_key == "home":
            return "WebSite"

        return "WebPage"

    mapping = {
        "product": "Product",
        "blog": "Article",
        "news": "NewsArticle",
        "media": "VideoObject",
        "resume": "Person",
        "tender": "CreativeWork",
        "holding": "Organization",
        "auction": "CreativeWork",
        "catalog": "CreativeWork",
        "hr": "JobPosting",
        "chart": "Organization",
        "other": "WebPage",
    }

    return mapping.get(
        content_type,
        "WebPage",
    )


# =====================================================
# Main schema generator
# =====================================================

def generate_schema(seo, obj=None):
    if seo is None:
        return {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": _site_name(),
        }

    # Manually configured JSON-LD takes precedence.
    manual = _get(seo, "schema_json")

    if manual:
        if isinstance(manual, str):
            try:
                parsed = json.loads(manual)
            except (TypeError, ValueError):
                parsed = None

            if isinstance(parsed, (dict, list)):
                return parsed

        elif isinstance(manual, (dict, list)):
            return manual

    schema_type = _resolve_schema_type(seo)

    content_type = (
        _get(seo, "content_type")
        or "page"
    )

    page_key = (
        _get(seo, "page_key")
        or ""
    )

    if (
        content_type == "page"
        and page_key == "home"
    ):
        return _build_home_graph(seo)

    if content_type == "product":
        main = _build_product(seo, obj)

    elif content_type == "blog":
        main = _build_article(
            seo,
            obj,
            schema_type="Article",
        )

    elif content_type == "news":
        main = _build_article(
            seo,
            obj,
            schema_type="NewsArticle",
        )

    elif content_type == "resume":
        main = _build_person(seo, obj)

    elif content_type == "media":
        main = _build_video(seo, obj)

    elif schema_type == "AboutPage":
        main = _build_web_page(
            seo,
            schema_type="AboutPage",
        )

    elif schema_type == "ContactPage":
        main = _build_web_page(
            seo,
            schema_type="ContactPage",
        )

    elif schema_type == "WebSite":
        main = _build_website()

    else:
        main = _build_web_page(
            seo,
            schema_type=schema_type or "WebPage",
        )

    breadcrumb = _get(
        seo,
        "breadcrumb",
    )

    if breadcrumb:
        breadcrumb_schema = (
            _build_breadcrumb_schema(
                breadcrumb
            )
        )

        if breadcrumb_schema:
            main["breadcrumb"] = breadcrumb_schema

    main["@context"] = "https://schema.org"

    return main
