
from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from app_product.models import Product

from app_product.views import (
    product_list,
    product_list_by_form,
    product_single,
    product_search,
    product_tag,
    scan_product,
)

app_name = "app_product"


def legacy_product_redirect(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        status="published"
    )
    return redirect(
        product.get_absolute_url(),
        permanent=True
    )


urlpatterns = [
    path("", product_list, name="product_list"),

    path(
        "scan/<str:sku>/",
        scan_product,
        name="scan"
    ),

    path(
        "search/",
        product_search,
        name="product_search"
    ),

    path(
        "category/<str:slug>/",
        product_list,
        name="category"
    ),

    path(
        "form/<str:slug>/",
        product_list_by_form,
        name="category_form"
    ),

    path(
        "tag/<str:slug>/",
        product_tag,
        name="product_tag"
    ),

    # Old numeric URLs: /product/3/
    path(
        "<int:pk>/",
        legacy_product_redirect,
        name="legacy_product_redirect"
    ),

    # New descriptive URLs
    path(
        "<str:slug>/",
        product_single,
        name="product_single"
    ),
]
