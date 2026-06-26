import platform
import sys
import django
import random
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.utils import timezone

from app_blog.models import blog
from app_news.models import News
from app_product.models import Product, ProductCategory
from app_media.models import Media
from app_banner.models import HeroBanner, OtherBanner
from app_tender.models import Tender
from app_auction.models import Auction
from app_hr.models import JobOpportunity, JobApplication


# ─────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("/dp-admin/dashboard/")

    error = None
    captcha_q = request.session.get("captcha_q", "")

    if request.method == "GET":
        a, b = random.randint(1, 9), random.randint(1, 9)
        request.session["captcha"] = a + b
        request.session["captcha_q"] = f"{a} + {b}"
        captcha_q = request.session["captcha_q"]

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        try:
            answer = int(request.POST.get("captcha_answer", ""))
        except ValueError:
            answer = None

        if answer != request.session.get("captcha"):
            error = "پاسخ سوال امنیتی اشتباه است."
        else:
            user = authenticate(request, username=username, password=password)
            if user and user.is_staff:
                auth_login(request, user)
                next_url = request.POST.get("next", "/dp-admin/dashboard/")
                return redirect(next_url)
            else:
                error = "نام کاربری یا رمز عبور اشتباه است."

        a, b = random.randint(1, 9), random.randint(1, 9)
        request.session["captcha"] = a + b
        request.session["captcha_q"] = f"{a} + {b}"
        captcha_q = request.session["captcha_q"]

    return render(request, "admin/login.html", {
        "captcha_q": captcha_q,
        "error": error,
        "next": request.GET.get("next", "/dp-admin/dashboard/"),
    })


# ─────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────
def admin_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("/dp-admin/login/")


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────
@staff_member_required(login_url="/dp-admin/login/")
def admin_dashboard(request):
    stats = [
        {
            "label": "محصولات",
            "count": Product.objects.count(),
            "published": Product.objects.filter(status="published").count(),
            "icon": "ti-pill",
            "color": "#1e40af",
            "bg": "#eff6ff",
            "url": "/admin/app_product/product/",
        },
        {
            "label": "بلاگ",
            "count": blog.objects.count(),
            "published": blog.objects.filter(status="published").count(),
            "icon": "ti-pencil",
            "color": "#7c3aed",
            "bg": "#f5f3ff",
            "url": "/admin/app_blog/blog/",
        },
        {
            "label": "اخبار",
            "count": News.objects.count(),
            "published": News.objects.filter(status="published").count(),
            "icon": "ti-speakerphone",
            "color": "#0891b2",
            "bg": "#ecfeff",
            "url": "/admin/app_news/news/",
        },
        {
            "label": "رسانه",
            "count": Media.objects.count(),
            "published": Media.objects.filter(status="published").count(),
            "icon": "ti-movie",
            "color": "#dc2626",
            "bg": "#fef2f2",
            "url": "/admin/app_media/media/",
        },
        {
            "label": "مناقصه",
            "count": Tender.objects.count(),
            "published": Tender.objects.filter(status="published").count(),
            "icon": "ti-file-text",
            "color": "#059669",
            "bg": "#ecfdf5",
            "url": "/admin/app_tender/tender/",
        },
        {
            "label": "مزایده",
            "count": Auction.objects.count(),
            "published": Auction.objects.filter(status="published").count(),
            "icon": "ti-gavel",
            "color": "#d97706",
            "bg": "#fffbeb",
            "url": "/admin/app_auction/auction/",
        },
        {
            "label": "فرصت شغلی",
            "count": JobOpportunity.objects.count(),
            "published": JobOpportunity.objects.filter(is_active=True).count(),
            "icon": "ti-briefcase",
            "color": "#be185d",
            "bg": "#fdf2f8",
            "url": "/admin/app_hr/jobopportunity/",
        },
        {
            "label": "درخواست شغلی",
            "count": JobApplication.objects.count(),
            "published": 0,
            "icon": "ti-file-cv",
            "color": "#0f766e",
            "bg": "#f0fdfa",
            "url": "/admin/app_hr/jobapplication/",
        },
    ]

    return render(request, "admin/dashboard.html", {
        "stats": stats,
        "server_info": {
            "python": sys.version.split()[0],
            "django": django.__version__,
            "os": platform.system() + " " + platform.release(),
            "time": timezone.now().strftime("%Y-%m-%d %H:%M"),
        },
    })