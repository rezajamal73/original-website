# app_sale/urls_en.py
from django.urls import path
from .views import sales_chart_view

app_name = "app_sale_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/sale/ از urls.py اصلی میاد)
    # =====================================================
    path("sales-chart/", sales_chart_view, name="sales_chart_en"),
]