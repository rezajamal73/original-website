# app_seo/schema.py

import json

from django.conf import settings


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get(obj, *names, default=None):
    """خواندن امن یک attribute از SEOSetting یا SEOContext."""
    if obj is None:
        return default
    for name in names:
        value = getattr(obj, name, None)
        if value is not None and value != "":
            return value
    return default


def _absolute_url(value):
    if not value:
        return ""

    if value.startswith(("http://", "https://")):
        return value

    base = getattr(settings, "SITE_URL", "").rstrip("/")

    if base:
        return f"{base}{value}"

    return value


def _site_name():
    return getattr(settings, "SITE_NAME", "Site")


def _site_logo():
    return getattr(settings, "SITE_LOGO_URL", "")


def _social_links():
    return getattr(settings, "SITE_SOCIAL_LINKS", [])


def _site_language():
    return getattr(settings, "LANGUAGE_CODE", "fa")


# =====================================================
#  BreadcrumbList
# =====================================================

def _build_breadcrumb_schema(breadcrumb_items):
    if not breadcrumb_items:
        return None

    elements = []

    for item in breadcrumb_items:
        entry = {
            "@type": "ListItem",
            "position": item.get("position", 1),
            "name": item.get("label", ""),
        }

        url = item.get("url")
        if url:
            entry["item"] = _absolute_url(url)

        elements.append(entry)

    return {
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


# =====================================================
#  Organization
# =====================================================

def _build_organization():
    org = {
        "@type": "Organization",
        "name": _site_name(),
        "url": _absolute_url("/"),
    }

    logo = _site_logo()
    if logo:
        org["logo"] = _absolute_url(logo)

    socials = _social_links()
    if socials:
        org["sameAs"] = socials

    return org


# =====================================================
#  WebSite
# =====================================================

def _build_website():
    return {
        "@type": "WebSite",
        "name": _site_name(),
        "url": _absolute_url("/"),
    }


# =====================================================
#  Home Graph  —  Organization + WebSite
# =====================================================

def _build_home_graph(seo=None):
    graph = [
        _build_organization(),
        _build_website(),
    ]

    # اگر SEO تنظیم شده بود، WebPage هم اضافه کن
    if seo is not None:
        page = _build_web_page(seo, schema_type="WebPage")
        if page:
            graph.append(page)

    return {
        "@context": "https://schema.org",
        "@graph": graph,
    }


# =====================================================
#  WebPage پایه
# =====================================================

def _build_web_page(seo, schema_type="WebPage"):
    page = {
        "@type": schema_type,
        "name": _get(seo, "title") or _site_name(),
        "description": _get(seo, "description") or "",
    }

    url = _get(seo, "canonical", "url")
    if url:
        page["url"] = _absolute_url(url)

    # زبان
    in_language = _get(seo, "language") or _site_language()
    if in_language:
        page["inLanguage"] = in_language

    return page


# =====================================================
#  Product + Offer
# =====================================================

def _build_product(seo, obj):
    product = {
        "@type": "Product",
        "name": _get(seo, "title") or _get(obj, "title_fa", "title_en", "title"),
        "description": _get(seo, "description") or _get(
            obj, "description_fa", "description_en", "description"
        ),
    }

    url = _get(seo, "canonical", "url")
    if url:
        product["url"] = _absolute_url(url)

    # تصویر
    image = None
    if obj is not None:
        img = getattr(obj, "image", None)
        if img:
            try:
                image = img.url
            except Exception:
                image = None

    if image:
        product["image"] = _absolute_url(image)

    # برند
    brand = _get(obj, "brand", "brand_name") if obj is not None else None
    if brand:
        product["brand"] = {
            "@type": "Brand",
            "name": str(brand),
        }

    # SKU / شناسه
    if obj is not None:
        sku = getattr(obj, "sku", None) or getattr(obj, "code", None)
        if sku:
            product["sku"] = str(sku)

    # قیمت
    if obj is not None:
        price = (
            getattr(obj, "price", None)
            or getattr(obj, "final_price", None)
            or getattr(obj, "sale_price", None)
        )

        currency = getattr(obj, "currency", None) or "IRR"

        if price:
            offer = {
                "@type": "Offer",
                "price": str(price),
                "priceCurrency": str(currency),
                "url": _absolute_url(url or ""),
                "availability": "https://schema.org/InStock",
            }

            updated = getattr(obj, "updated_at", None)
            if updated:
                try:
                    offer["priceValidUntil"] = updated.date().isoformat()
                except Exception:
                    pass

            product["offers"] = offer

    return product


# =====================================================
#  Article / NewsArticle
# =====================================================

def _build_article(seo, obj, schema_type="Article"):
    article = {
        "@type": schema_type,
        "headline": _get(seo, "title") or _get(obj, "title_fa", "title_en", "title"),
        "description": _get(seo, "description") or _get(
            obj, "description_fa", "description_en", "description"
        ),
    }

    url = _get(seo, "canonical", "url")
    if url:
        article["mainEntityOfPage"] = {
            "@type": "WebPage",
            "@id": _absolute_url(url),
        }
        article["url"] = _absolute_url(url)

    # تصویر
    if obj is not None:
        img = (
            getattr(obj, "image", None)
            or getattr(obj, "cover", None)
            or getattr(obj, "thumbnail", None)
        )
        if img:
            try:
                article["image"] = _absolute_url(img.url)
            except Exception:
                pass

    # تاریخ‌ها
    if obj is not None:
        published = (
            getattr(obj, "publish_date", None)
            or getattr(obj, "publish_date_fa", None)
            or getattr(obj, "publish_date_en", None)
            or getattr(obj, "created_at", None)
        )
        if published:
            try:
                article["datePublished"] = published.isoformat()
            except Exception:
                pass

        updated = getattr(obj, "updated_at", None)
        if updated:
            try:
                article["dateModified"] = updated.isoformat()
            except Exception:
                pass

    # نویسنده
    if obj is not None:
        author = getattr(obj, "author", None)
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

    # زبان
    in_language = _get(seo, "language") or _site_language()
    if in_language:
        article["inLanguage"] = in_language

    return article


# =====================================================
#  Person / Resume
# =====================================================

def _build_person(seo, obj):
    person = {
        "@type": "Person",
        "name": _get(seo, "title") or _get(obj, "full_name", "name"),
    }

    if obj is not None:
        job_title = getattr(obj, "job_title", None) or getattr(obj, "position", None)
        if job_title:
            person["jobTitle"] = str(job_title)

        email = getattr(obj, "email", None)
        if email:
            person["email"] = str(email)

        phone = getattr(obj, "phone", None)
        if phone:
            person["telephone"] = str(phone)

    return person


# =====================================================
#  VideoObject / Media
# =====================================================

def _build_video(seo, obj):
    video = {
        "@type": "VideoObject",
        "name": _get(seo, "title"),
        "description": _get(seo, "description"),
    }

    url = _get(seo, "canonical", "url")
    if url:
        video["url"] = _absolute_url(url)

    if obj is not None:
        thumb = getattr(obj, "thumbnail", None) or getattr(obj, "image", None)
        if thumb:
            try:
                video["thumbnailUrl"] = _absolute_url(thumb.url)
            except Exception:
                pass

        upload = (
            getattr(obj, "publish_date", None)
            or getattr(obj, "created_at", None)
        )
        if upload:
            try:
                video["uploadDate"] = upload.isoformat()
            except Exception:
                pass

    return video


# =====================================================
#  انتخاب نوع schema بر اساس content_type / page_key
# =====================================================

def _resolve_schema_type(seo):
    explicit = _get(seo, "schema_type")

    if explicit and explicit != "auto":
        return explicit

    content_type = _get(seo, "content_type") or "page"
    page_key = _get(seo, "page_key") or ""

    if content_type == "page":
        if page_key == "about":
            return "AboutPage"
        if page_key in ("contact", "contact_security"):
            return "ContactPage"
        if page_key in ("search", "404"):
            return "WebPage"
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

    return mapping.get(content_type, "WebPage")


# =====================================================
#  generate_schema  —  نقطه ورود عمومی
# =====================================================

def generate_schema(seo, obj=None):
    """
    امضای عمومی:
        generate_schema(seo, obj=None) -> dict

    هم SEOContext و هم SEOSetting خام پذیرفته می‌شود.
    اگر seo هیچ‌کدام نباشد، یک WebPage حداقلی برمی‌گرداند.
    """

    if seo is None:
        return {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": _site_name(),
        }

    # ---------- Schema دستی ----------

    manual = _get(seo, "schema_json")
    if manual:
        if isinstance(manual, str):
            try:
                return json.loads(manual)
            except (TypeError, ValueError):
                pass
        elif isinstance(manual, dict):
            return manual

    schema_type = _resolve_schema_type(seo)
    content_type = _get(seo, "content_type") or "page"
    page_key = _get(seo, "page_key") or ""

    # ---------- Home  →  @graph ----------

    if content_type == "page" and page_key == "home":
        return _build_home_graph(seo)

    # ---------- انتخاب generator ----------

    if content_type == "product":
        main = _build_product(seo, obj)

    elif content_type == "blog":
        main = _build_article(seo, obj, schema_type="Article")

    elif content_type == "news":
        main = _build_article(seo, obj, schema_type="NewsArticle")

    elif content_type == "resume":
        main = _build_person(seo, obj)

    elif content_type == "media":
        main = _build_video(seo, obj)

    elif schema_type == "AboutPage":
        main = _build_web_page(seo, schema_type="AboutPage")

    elif schema_type == "ContactPage":
        main = _build_web_page(seo, schema_type="ContactPage")

    elif schema_type == "WebSite":
        main = _build_website()

    else:
        main = _build_web_page(seo, schema_type=schema_type or "WebPage")

    # ---------- Breadcrumb ----------

    breadcrumb = _get(seo, "breadcrumb")

    if breadcrumb:
        bc_schema = _build_breadcrumb_schema(breadcrumb)
        if bc_schema:
            main["breadcrumb"] = bc_schema

    # ---------- @context ----------

    main["@context"] = "https://schema.org"

    return main