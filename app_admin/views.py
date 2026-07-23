import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from app_reports.models import SiteMainInfo


def generate_captcha(request):
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    request.session["captcha"] = a + b
    request.session["captcha_q"] = f"{a} + {b}"


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("/admin/")

    # اطلاعات سایت (لوگو و ...)
    site_info = SiteMainInfo.objects.first()

    error = None

    if request.method == "GET":
        generate_captcha(request)

    elif request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        try:
            answer = int(request.POST.get("captcha_answer", ""))
        except (TypeError, ValueError):
            answer = None

        if answer != request.session.get("captcha"):
            error = "پاسخ سوال امنیتی اشتباه است."
            generate_captcha(request)

        else:
            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user and user.is_staff:
                login(request, user)
                return redirect(request.POST.get("next", "/admin/"))

            error = "نام کاربری یا رمز عبور اشتباه است."
            generate_captcha(request)

    return render(
        request,
        "admin/login.html",
        {
            "site_info": site_info,
            "captcha_q": request.session.get("captcha_q"),
            "error": error,
            "next": request.GET.get("next", "/admin/"),
        },
    )