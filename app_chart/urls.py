from django.urls import path
from app_chart import views

app_name = "app_chart"

urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    # چارت سازمانی
    path(
        "",
        views.orgchart_tree,
        name="chart",
    ),

    path(
        "person/<int:pid>/",
        views.person_detail,
        name="person_detail",
    ),


    # هیأت‌مدیره
    path(
        "board/",
        views.board_home,
        name="board_home",
    ),

    path(
        "board/<int:pid>/",
        views.board_single,
        name="board_single",
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    # Organizational Chart
    path(
        "en/",
        views.orgchart_tree,
        name="chart_en",
    ),

    path(
        "en/person/<int:pid>/",
        views.person_detail,
        name="person_detail_en",
    ),


    # Board of Directors
    path(
        "en/board/",
        views.board_home,
        name="board_home_en",
    ),

    path(
        "en/board/<int:pid>/",
        views.board_single,
        name="board_single_en",
    ),
]