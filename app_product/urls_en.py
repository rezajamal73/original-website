from django.urls import path

from app_product.views import (
    product_list,
    product_list_by_form,
    product_single,
    product_single_redirect,
    product_search,
    product_tag,
    scan_product,
)

app_name = "app_product_en"

urlpatterns = [
    path("", product_list, name="product_list_en"),
    path("scan/<str:sku>/", scan_product, name="scan_en"),
    path("search/", product_search, name="product_search_en"),
    path("category/<slug:slug>/", product_list, name="category_en"),
    path("form/<slug:slug>/", product_list_by_form, name="category_form_en"),
    path("tag/<slug:slug>/", product_tag, name="product_tag_en"),
    path("<int:pid>/", product_single_redirect, name="product_single_old_en"),
    path("<int:pid>/<slug:slug>/", product_single, name="product_single_en"),
]