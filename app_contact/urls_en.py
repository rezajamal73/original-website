# app_contact/urls_en.py
from django.urls import path
from .views import contact_submit

app_name = "app_contact_en"

urlpatterns = [
    path("submit/", contact_submit, name="contact_submit_en"),
]