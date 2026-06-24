from django.urls import path
from app_core.views import *

app_name = "app_core"

urlpatterns = [
    path("", home, name="home"),
    path("category/<slug:slug>/", home, name="category"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
    path("contact_security/", contact_security, name="contact_security"),
    path("search/", search, name="search"),
    path("404/", error, name="404"),

    path("en/", home_en, name="home_en"),

]
