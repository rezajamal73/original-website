from django.urls import path
from app_chart import views

app_name = "app_chart"

urlpatterns = [
    # -------------------------
    #  چارت سازمانی
    # -------------------------
    path("", views.orgchart_tree, name="chart"),
    path("person/<int:pid>/", views.person_detail, name="person_detail"),

    # -------------------------
    #  هیأت‌مدیره
    # -------------------------
    path("board/", views.board_home, name="board_home"),
    path("board/<int:pid>/", views.board_single, name="board_single"),
]
