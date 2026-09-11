
from django.urls import path

from app_product.views import (
    product_list,
    product_list_by_form,
    product_single,
    product_search,
    product_tag,
    scan_product,
)

app_name = "app_product"


urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    # Product List
    path(
        "",
        product_list,
        name="product_list",
    ),

    # QR
    path(
        "scan/<str:sku>/",
        scan_product,
        name="scan",
    ),

    # Search
    path(
        "search/",
        product_search,
        name="product_search",
    ),

    # Filters
    path(
        "category/<slug:slug>/",
        product_list,
        name="category",
    ),

    path(
        "form/<slug:slug>/",
        product_list_by_form,
        name="category_form",
    ),

    path(
        "tag/<slug:slug>/",
        product_tag,
        name="product_tag",
    ),

    # Single
    path(
        "<int:pid>/",
        product_single,
        name="product_single",
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    # Product List
    path(
        "en/",
        product_list,
        name="product_list_en",
    ),

    # QR
    path(
        "en/scan/<str:sku>/",
        scan_product,
        name="scan_en",
    ),

    # Search
    path(
        "en/search/",
        product_search,
        name="product_search_en",
    ),

    # Filters
    path(
        "en/category/<slug:slug>/",
        product_list,
        name="category_en",
    ),

    path(
        "en/form/<slug:slug>/",
        product_list_by_form,
        name="category_form_en",
    ),

    path(
        "en/tag/<slug:slug>/",
        product_tag,
        name="product_tag_en",
    ),

    # Single
    path(
        "en/<int:pid>/",
        product_single,
        name="product_single_en",
    ),
]

