from django.urls import path
from . import views

app_name = "app_media_en"

urlpatterns = [
    path("", views.media_home, name="home_en"),
    path("<int:pk>/", views.media_single, name="single_en"),
]