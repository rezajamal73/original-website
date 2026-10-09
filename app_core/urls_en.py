from django.urls import path
from app_core.views import *

app_name = "app_core_en"


urlpatterns = [

    # =====================================================
    # ENGLISH  (prefix: /en/ از urls.py اصلی میاد)
    # =====================================================

    path("", home, name="home_en"),
    path("category/<slug:slug>/", home, name="category_en"),
    path("about/", about, name="about_en"),
    path("contact/", contact, name="contact_en"),
    path("contact_security/", contact_security, name="contact_security_en"),
    path("search/", search, name="search_en"),
    path("404/", error, name="404_en"),
]