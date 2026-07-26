from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from app_reports.models import SiteMainInfo
from .forms import AdminLoginForm


def admin_login(request):
    # اگر قبلاً وارد شده باشد
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("/admin/")

    site_info = SiteMainInfo.objects.first()
    error = None

    if request.method == "POST":
        form = AdminLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user and user.is_staff:
                login(request, user)
                return redirect(request.POST.get("next") or "/admin/")

            error = "نام کاربری یا رمز عبور اشتباه است."

    else:
        form = AdminLoginForm()

    return render(
        request,
        "admin/login.html",
        {
            "site_info": site_info,
            "form": form,
            "error": error,
            "next": request.GET.get("next", "/admin/"),
        },
    )