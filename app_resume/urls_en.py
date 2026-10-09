from django.urls import path

from . import views

app_name = "app_resume_en"

urlpatterns = [
    # =====================================================
    # ENGLISH  (prefix: /en/resume/ از urls.py اصلی میاد)
    # =====================================================

    path("", views.resume_home, name="resume_en"),
]