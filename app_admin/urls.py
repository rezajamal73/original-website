from django.contrib import admin
from django.urls import path, include

from .views import admin_login

urlpatterns = [
    # صفحه لاگین سفارشی
    path("admin/login/", admin_login, name="admin_login"),

    # آدرس کپچا
    path("captcha/", include("captcha.urls")),

    # پنل مدیریت (همیشه آخر باشد)
    path("admin/", admin.site.urls),
]