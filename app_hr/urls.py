# app_hr/urls.py
from django.urls import path
from app_hr.views import hr_home, hr_single

app_name = "app_hr"

urlpatterns = [
    path("", hr_home, name="hr_home"),
    path("<str:slug>/", hr_single, name="hr_single"),   # ✅ slug جای pid
]