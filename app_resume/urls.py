from django.urls import path

from . import views

app_name = "app_resume"

urlpatterns = [
    path("", views.resume_home, name="resume"),
]