# app_seo/views.py

from django.conf import settings
from django.http import HttpResponse


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