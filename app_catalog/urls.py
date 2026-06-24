from django.urls import path
from .views import company_catalog_view

app_name = "app_catalog"

urlpatterns = [
    path("", company_catalog_view, name="catalog"),
]
