
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


    # =====================================================
    # ENGLISH
    # =====================================================

    # Media Home
    path(
        "en/",
        views.media_home,
        name="home_en",
    ),

    # Media Single
    path(
        "en/<int:pk>/",
        views.media_single,
        name="single_en",
    ),
]

