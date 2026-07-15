from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("admin/login/", admin_login, name="admin_login"),
    path("admin/", admin.site.urls),  # این باید آخرین باشد
]