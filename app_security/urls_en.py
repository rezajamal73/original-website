from django.urls import path
from .views import security_contact

app_name = "app_security_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/security_contact/ از urls.py اصلی میاد)
    # =====================================================

    path("security_contact/", security_contact, name="security_contact_en"),
]