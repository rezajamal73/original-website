
# app_catalog/views.py

from django.shortcuts import render

from .models import CompanyCatalog
from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English pages based on URL name.

    Persian:
        catalog

    English:
        catalog_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


# =====================================================
# COMPANY CATALOG
# =====================================================

def company_catalog_view(request):

    is_english = is_english_request(request)

    catalog = CompanyCatalog.objects.first()

    template_name = (
        "LTR/catalog/catalog.html"
        if is_english
        else "RTL/catalog/catalog.html"
    )

    context = {
        "catalog": catalog,
        "seo": SEOManager.get_page("catalog"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context
    )

