
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.utils.http import url_has_allowed_host_and_scheme

from app_reports.models import SiteMainInfo
from .forms import AdminLoginForm


def admin_login(request):
    # اگر مدیر قبلاً وارد شده باشد
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

                target = request.POST.get("next") or "/admin/"

                if not url_has_allowed_host_and_scheme(
                    url=target,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    target = "/admin/"

                return redirect(target)

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
