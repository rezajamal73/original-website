from django.urls import path
from . import views

app_name = "app_admin"

urlpatterns = [
    path("login/",     views.admin_login,     name="login"),
    path("logout/",    views.admin_logout,    name="logout"),
    path("dashboard/", views.admin_dashboard, name="dashboard"),
]