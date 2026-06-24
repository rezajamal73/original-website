from django.urls import path
from .views import security_contact

app_name = "app_security"

urlpatterns = [
    path("security_contact/", security_contact, name="security_contact"),
]
