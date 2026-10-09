from django.urls import path
from . import views

app_name = "app_media"

urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    # Media Home
    path(
        "",
        views.media_home,
        name="home",
    ),

    # Media Single
    path(
        "<int:pk>/",
        views.media_single,
        name="single",
    ),
]