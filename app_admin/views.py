
import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("/admin/")

    error = None
    captcha_q = request.session.get("captcha_q", "")

    # تولید کپچای جدید برای GET
    if request.method == "GET":
        a, b = random.randint(1, 9), random.randint(1, 9)
        request.session["captcha"] = a + b
        request.session["captcha_q"] = f"{a} + {b}"
        captcha_q = request.session["captcha_q"]

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        # بررسی کپچا
        try:
            answer = int(request.POST.get("captcha_answer", ""))
        except ValueError:
            answer = None

        if answer != request.session.get("captcha"):
            error = "پاسخ سوال امنیتی اشتباه است."
            # کپچای جدید بساز
            a, b = random.randint(1, 9), random.randint(1, 9)
            request.session["captcha"] = a + b
            request.session["captcha_q"] = f"{a} + {b}"
            captcha_q = request.session["captcha_q"]
        else:
            user = authenticate(request, username=username, password=password)
            if user and user.is_staff:
                auth_login(request, user)
                next_url = request.POST.get("next", "/admin/")
                return redirect(next_url)
            else:
                error = "نام کاربری یا رمز عبور اشتباه است."
                # کپچای جدید بساز
                a, b = random.randint(1, 9), random.randint(1, 9)
                request.session["captcha"] = a + b
                request.session["captcha_q"] = f"{a} + {b}"
                captcha_q = request.session["captcha_q"]

    return render(request, "admin/login.html", {
        "captcha_q": captcha_q,
        "error": error,
        "next": request.GET.get("next", "/admin/"),
    })

