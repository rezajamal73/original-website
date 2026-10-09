from django.urls import path

from .views import company_catalog_view

app_name = "app_catalog_en"


urlpatterns = [

    # =====================================================
    # ENGLISH  (prefix: /en/catalog/ از urls.py اصلی میاد)
    # =====================================================

    path(
        "",
        company_catalog_view,
        name="catalog_en",
    ),
]