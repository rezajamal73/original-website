# app_contact/urls.py
from django.urls import path
from .views import contact_submit

app_name = "app_contact"

urlpatterns = [
    path("submit/", contact_submit, name="contact_submit"),
]
