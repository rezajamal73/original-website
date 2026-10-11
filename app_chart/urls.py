# app_chart/urls.py
from django.urls import path
from app_chart import views

app_name = "app_chart"

urlpatterns = [
    # =====================================================
    # PERSIAN  (prefix: /chart/ از urls.py اصلی میاد)
    # =====================================================

    # چارت سازمانی
    path("", views.orgchart_tree, name="chart"),

    # ✅ URL جدید: /chart/person/نام-فرد/  (بدون pid)
    path("person/<str:slug>/", views.person_detail, name="person_detail"),

    # هیأت‌مدیره
    path("board/", views.board_home, name="board_home"),

    # ✅ URL جدید: /chart/board/نام-عضو/  (بدون pid)
    path("board/<str:slug>/", views.board_single, name="board_single"),
]