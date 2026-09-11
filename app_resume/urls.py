
from django.urls import path

from . import views

app_name = "app_resume"


urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path(
        "",
        views.resume_home,
        name="resume",
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    path(
        "en/",
        views.resume_home,
        name="resume_en",
    ),
]

