# app_sale/urls.py
from django.urls import path
from .views import sales_chart_view

app_name = "app_sale"

urlpatterns = [
    # =====================================================
    # PERSIAN
    # =====================================================
    path("sales-chart/", sales_chart_view, name="sales_chart"),
]