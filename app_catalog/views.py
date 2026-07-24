# app_catalog/views.py

from django.shortcuts import render

from .models import CompanyCatalog
from app_seo.utils import SEOManager



# =====================================================
# COMPANY CATALOG
# =====================================================
def company_catalog_view(request):

    catalog = CompanyCatalog.objects.first()


    context = {
        "catalog": catalog,
        "seo": SEOManager.get_page("catalog"),
    }


    return render(
        request,
        "RTL/catalog/catalog.html",
        context
    )