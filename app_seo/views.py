# app_seo/views.py

from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.sitemaps.views import sitemap as django_sitemap

from app_seo.sitemaps import sitemaps

import xml.etree.ElementTree as ET


# ==========================================
# Robots.txt
# ==========================================

def robots_txt(request):
    """
    robots.txt داینامیک.

    - از SITE_URL در settings استفاده می‌کند.
    - مسیرهای admin, panel, search را از crawl خارج می‌کند.
    - آدرس sitemap را اعلام می‌کند.
    """

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")

    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /panel/",
        "Disallow: /search",
        "Disallow: /*?q=",
        "Disallow: /*?page=",
        "",
        f"Sitemap: {site_url}/sitemap.xml",
        "",
    ]

    return HttpResponse(
        "\n".join(lines),
        content_type="text/plain",
    )


# ==========================================
# Human-readable Sitemap
# ==========================================

def sitemap_view(request):
    """
    نمایش خوانای آدرس‌های سایت‌مپ.

    - سایت‌مپ اصلی گوگل را تغییر نمی‌دهد.
    - آدرس‌های فارسی را خوانا نمایش می‌دهد.
    - آدرس‌های انگلیسی را بدون تغییر نمایش می‌دهد.
    """

    response = django_sitemap(
        request,
        sitemaps=sitemaps,
    )

    if not response.is_rendered:
        response.render()

    root = ET.fromstring(response.content)

    namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }

    urls = []

    for item in root.findall("sm:url", namespace):

        loc = item.find("sm:loc", namespace)

        if loc is None or not loc.text:
            continue

        original_url = loc.text

        readable_url = unquote(original_url)

        urls.append({
            "url": original_url,
            "readable_url": readable_url,
        })

    return render(
        request,
        "seo/sitemap_view.html",
        {
            "urls": urls,
        },
    )