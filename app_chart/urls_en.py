from django.urls import path
from app_chart import views

app_name = "app_chart_en"

urlpatterns = [

    # =====================================================
    # ENGLISH  (prefix: /en/chart/ از urls.py اصلی میاد)
    # =====================================================

    # Organizational Chart
    path("", views.orgchart_tree, name="chart_en"),
    path("person/<int:pid>/", views.person_detail, name="person_detail_en"),

    # Board of Directors
    path("board/", views.board_home, name="board_home_en"),
    path("board/<int:pid>/", views.board_single, name="board_single_en"),
]