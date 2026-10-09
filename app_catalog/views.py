# app_catalog/views.py

from django.shortcuts import render

from .models import CompanyCatalog
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core میاد
from app_core.url_helpers import is_english_request


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