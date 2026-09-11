
from django.urls import path

from .views import company_catalog_view

app_name = "app_catalog"


urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path(
        "",
        company_catalog_view,
        name="catalog",
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    path(
        "en/",
        company_catalog_view,
        name="catalog_en",
    ),
]

