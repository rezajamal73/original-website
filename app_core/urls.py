from django.urls import path
from app_core.views import *

app_name = "app_core"

urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path(
        "",
        home,
        name="home"
    ),

    path(
        "category/<slug:slug>/",
        home,
        name="category"
    ),

    path(
        "about/",
        about,
        name="about"
    ),

    path(
        "contact/",
        contact,
        name="contact"
    ),

    path(
        "contact_security/",
        contact_security,
        name="contact_security"
    ),

    path(
        "search/",
        search,
        name="search"
    ),

    path(
        "404/",
        error,
        name="404"
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    path(
        "en/",
        home,
        name="home_en"
    ),

    path(
        "en/category/<slug:slug>/",
        home,
        name="category_en"
    ),

    path(
        "en/about/",
        about,
        name="about_en"
    ),

    path(
        "en/contact/",
        contact,
        name="contact_en"
    ),

    path(
        "en/contact_security/",
        contact_security,
        name="contact_security_en"
    ),

    path(
        "en/search/",
        search,
        name="search_en"
    ),

    path(
        "en/404/",
        error,
        name="404_en"
    ),
]