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
    path("", product_list, name="product_list"),

    # QR
    path("scan/<str:sku>/", scan_product, name="scan"),

    # Search
    path("search/", product_search, name="product_search"),

    # Filters
    path("category/<slug:slug>/", product_list, name="category"),
    path("form/<slug:slug>/", product_list_by_form, name="category_form"),
    path("tag/<slug:slug>/", product_tag, name="product_tag"),

    # Single
    path("<int:pid>/", product_single, name="product_single"),
]
