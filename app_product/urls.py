# app_product/urls.py
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

app_name = "app_product"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /product/ از urls.py اصلی میاد)
    # =====================================================

    # Product List
    path("", product_list, name="product_list"),

    # QR
    path("scan/<str:sku>/", scan_product, name="scan"),

    # Search
    path("search/", product_search, name="product_search"),

    # Filters — ✅ slug → str (پشتیبانی از فارسی)
    path("category/<str:slug>/", product_list, name="category"),
    path("form/<str:slug>/", product_list_by_form, name="category_form"),
    path("tag/<str:slug>/", product_tag, name="product_tag"),

    # ✅ Redirect از URL قدیمی /product/3/
    path("<int:pid>/", product_single_redirect, name="product_single_old"),

    # ✅ URL جدید: /product/3/آویز-سرم-بیمارستانی/
    path("<int:pid>/<str:slug>/", product_single, name="product_single"),   # ← slug → str
]