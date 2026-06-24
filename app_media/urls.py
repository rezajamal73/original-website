from django.urls import path
from . import views

app_name = "app_media"

urlpatterns = [
    # صفحه لیست همه بخش‌های رسانه
    path("", views.media_home, name="home"),

    # جزئیات یک بخش رسانه
    path("<int:pk>/", views.media_single, name="single"),
]
