
# app_seo/views.py

import logging
import xml.etree.ElementTree as ET

from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.http import HttpResponse
from django.shortcuts import render

from app_seo.sitemaps import sitemaps


logger = logging.getLogger(__name__)


# ============================================================
# Sitemap and site URL helpers
# ============================================================

SITEMAP_NAMESPACE = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
}


def _site_url(request):
    """
    Return the canonical site origin.

    Prefer the production SITE_URL setting.
    Never use an arbitrary Host header to generate the
    robots.txt sitemap URL.
    """

    configured_url = str(
        getattr(settings, "SITE_URL", "") or ""
    ).strip().rstrip("/")

    if configured_url:
        try:
            parts = urlsplit(configured_url)
        except ValueError:
            parts = None

        if (
            parts
            and parts.scheme == "https"
            and parts.hostname
            and not parts.username
            and not parts.password
        ):
            return (
                "https://"
                + parts.netloc
            )

    # Safe production fallback for this website.
    return "https://nkavosh.com"


def _read_sitemap_urls(xml_content):
    """
    Extract URL entries from Django's XML sitemap.

    This function does not modify the original sitemap.
    """

    if not xml_content:
        return []

    root = ET.fromstring(xml_content)

    urls = []
    seen = set()

    for item in root.findall(
        "sm:url",
        SITEMAP_NAMESPACE,
    ):
        loc = item.find(
            "sm:loc",
            SITEMAP_NAMESPACE,
        )

        if loc is None or not loc.text:
            continue

        original_url = loc.text.strip()

        if not original_url:
            continue

        try:
            parsed = urlsplit(original_url)
        except ValueError:
            continue

        # Only display valid HTTP(S) URLs.
        if parsed.scheme not in ("http", "https"):
            continue

        if not parsed.hostname:
            continue

        if parsed.username or parsed.password:
            continue

        if original_url in seen:
            continue

        seen.add(original_url)

        readable_url = unquote(original_url)

        urls.append(
            {
                "url": original_url,
                "readable_url": readable_url,
            }
        )

    return urls


# ============================================================
# Robots.txt
# ============================================================

def robots_txt(request):
    """
    Dynamic robots.txt for search engines.

    - Disallow administrative and private routes.
    - Disallow common internal search URLs.
    - Publish the canonical XML sitemap URL.
    """

    site_url = _site_url(request)

    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /panel/",
        "Disallow: /search",
        "Disallow: /en/admin/",
        "Disallow: /en/panel/",
        "Disallow: /en/search",
        "Disallow: /*?q=",
        "Disallow: /*?page=",
        "",
        f"Sitemap: {site_url}/sitemap.xml",
        "",
    ]

    response = HttpResponse(
        "\n".join(lines),
        content_type="text/plain; charset=utf-8",
    )

    response["X-Content-Type-Options"] = "nosniff"

    return response


# ============================================================
# Human-readable Sitemap
# ============================================================

def sitemap_view(request):
    """
    Display a human-readable version of the XML sitemap.

    The original /sitemap.xml route remains unchanged.

    The existing template receives a list of dictionaries
    containing:
        - url
        - readable_url
    """

    try:
        response = django_sitemap(
            request,
            sitemaps=sitemaps,
        )

        if hasattr(response, "render"):
            if not response.is_rendered:
                response.render()

        if response.status_code != 200:
            logger.warning(
                "Sitemap generation returned status %s",
                response.status_code,
            )

            return HttpResponse(
                "نقشه سایت در حال حاضر در دسترس نیست.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )

        urls = _read_sitemap_urls(
            response.content
        )

    except ET.ParseError:
        logger.exception(
            "Invalid XML while generating readable sitemap"
        )

        return HttpResponse(
            "خطا در پردازش نقشه سایت.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    except Exception:
        logger.exception(
            "Unexpected error in readable sitemap"
        )

        return HttpResponse(
            "نقشه سایت در حال حاضر در دسترس نیست.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    return render(
        request,
        "seo/sitemap_view.html",
        {
            "urls": urls,
        },
    )
