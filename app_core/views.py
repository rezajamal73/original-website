import random

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from app_banner.models import HeroBanner, OtherBanner, SpecialProductBanner, MainBanner, HeroSliderSetting
from app_blog.models import blog
from app_product.models import Product, ProductCategory
from app_reports.models import CorporateSection, CorporateStatistic, GroupCompany, FollowUsLink, SiteMainInfo
from app_media.models import Media

from app_news.models import News


def home(request, slug=None):
    banners = HeroBanner.objects.filter(
        status="published"
    ).order_by("order", "id")

    slider_setting = HeroSliderSetting.objects.first()

    active_slider = (
        slider_setting.active_slider
        if slider_setting else "hs_1"
    )

    blogs = blog.objects.filter(status="published").order_by(
        "-publish_date_fa", "-publish_date_en"
    )[:3]

    active_category = None
    product_filter = Q(status="published")

    if slug:
        active_category = get_object_or_404(ProductCategory, slug=slug)
        product_filter &= Q(category=active_category)

    special_products = (
        Product.objects
        .filter(product_filter, special=True)
        .order_by("priority", "title_fa")[:12]
    )

    special_product_banners = SpecialProductBanner.objects.filter(
        status="published"
    ).order_by("order", "created_at")[:4]

    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    statistics = CorporateStatistic.objects.filter(
        is_active=True
    ).order_by("display_order")

    about_section = (
        CorporateSection.objects
        .filter(section_type="about", is_published=True)
        .prefetch_related("texts", "about_items")
        .select_related("about_year")
        .first()
    )

    group_companies = GroupCompany.objects.filter(
        is_active=True
    ).order_by("display_order")

    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True, svg_icon__isnull=False, url__isnull=False)
        .exclude(url="")
        .order_by("display_order")
    )
    main_banner = MainBanner.objects.filter(status="published").first()
    site_info = SiteMainInfo.objects.first()  # ✅ مهم
    home_medias = (
        Media.objects
        .filter(
            status="published",  # ✅ منتشر شده
            is_special=True,  # ✅ نمایش در صفحه اصلی
        )
        .prefetch_related("images", "videos")
        .order_by("order")
    )
    context = {
        "banners": banners,
        "active_slider": active_slider,
        "blogs": blogs,
        "special_products": special_products,
        "special_product_banners": special_product_banners,
        "categories": categories,
        "active_category": active_category,
        "statistics": statistics,
        "section": about_section,
        "group_companies": group_companies,
        "follow_links": follow_links,
        "site_info": site_info,
        "home_medias": home_medias,
        "main_banner": main_banner,
    }

    return render(request, "RTL/core/home.html", context)


def about(request):
    banner = OtherBanner.objects.filter(status="published").first()

    section = (
        CorporateSection.objects
        .prefetch_related(
            "texts__images",
            "texts__attachments",
        )
        .filter(
            section_type="history",
            is_published=True,
        )
        .first()
    )
    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )
    site_info = SiteMainInfo.objects.first()  # ✅ اضافه شد

    context = {
        "categories": categories,
        "banner": banner,
        "section": section,
        "site_info": site_info,  # ✅ مهم
    }

    return render(request, "RTL/core/history.html", context)


def _generate_captcha():
    return "".join(random.choice("0123456789") for _ in range(5))


def contact(request):
    banner = OtherBanner.objects.filter(status="published").first()
    site_info = SiteMainInfo.objects.first()

    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True)
        .exclude(url="")
        .exclude(svg_icon="")
        .order_by("display_order")
    )

    # ✅ ساخت کپچا برای نمایش
    if "contact_captcha" not in request.session:
        request.session["contact_captcha"] = _generate_captcha()
        request.session.modified = True

    context = {
        "categories": categories,
        "banner": banner,
        "follow_links": follow_links,
        "site_info": site_info,
        "captcha_code": request.session["contact_captcha"],  # ⭐ حیاتی
    }

    return render(request, "RTL/core/contact.html", context)


def contact_security(request):
    banner = OtherBanner.objects.filter(status="published").first()
    site_info = SiteMainInfo.objects.first()

    follow_links = (
        FollowUsLink.objects
        .filter(
            is_active=True,
            svg_icon__isnull=False,
            url__isnull=False,
        )
        .exclude(url="")
        .order_by("display_order")
    )

    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )

    # ✅ ساخت کپچا برای نمایش (دقیقاً مثل contact)
    if "security_captcha" not in request.session:
        request.session["security_captcha"] = _generate_captcha()
        request.session.modified = True

    context = {
        "categories": categories,
        "banner": banner,
        "follow_links": follow_links,
        "site_info": site_info,
        "captcha_code": request.session["security_captcha"],  # ⭐ حیاتی
    }

    return render(
        request,
        "RTL/core/contact_security.html",
        context
    )


def error(request):
    banner = OtherBanner.objects.filter(status="published").first()
    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")
    )
    follow_links = (
        FollowUsLink.objects
        .filter(
            is_active=True,
            svg_icon__isnull=False,
            url__isnull=False,
        )
        .exclude(url="")
        .order_by("display_order")
    )

    context = {
        "categories": categories,
        "banner": banner,
        "follow_links": follow_links,
    }

    return render(request, "../templates/404.html", context)


def home_en(request, slug=None):
    # =======================
    # HERO BANNERS
    # =======================
    banners = HeroBanner.objects.filter(
        status="published"
    ).order_by("order", "id")

    slider_setting = HeroSliderSetting.objects.first()
    active_slider = slider_setting.active_slider if slider_setting else "hs_1"

    # =======================
    # BLOGS
    # =======================
    blogs = blog.objects.filter(
        status="published"
    ).order_by(
        "-publish_date_en",
        "-publish_date_fa",
    )[:3]

    # =======================
    # PRODUCTS
    # =======================
    active_category = None
    product_filter = Q(status="published")

    if slug:
        active_category = get_object_or_404(ProductCategory, slug=slug)
        product_filter &= Q(category=active_category)

    special_products = (
        Product.objects
        .filter(product_filter, special=True)
        .order_by("priority", "title_en")[:12]
    )

    # =======================
    # SPECIAL PRODUCT BANNERS
    # =======================
    special_product_banners = SpecialProductBanner.objects.filter(
        status="published"
    ).order_by("order", "created_at")[:4]

    # =======================
    # CATEGORIES
    # =======================
    categories = (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_en")
    )

    # =======================
    # STATISTICS
    # =======================
    statistics = CorporateStatistic.objects.filter(
        is_active=True
    ).order_by("display_order")

    # =======================
    # ABOUT SECTION
    # =======================
    about_section = (
        CorporateSection.objects
        .filter(section_type="about", is_published=True)
        .prefetch_related("texts", "about_items")
        .select_related("about_year")
        .first()
    )

    # =======================
    # GROUP COMPANIES
    # =======================
    group_companies = GroupCompany.objects.filter(
        is_active=True
    ).order_by("display_order")

    # =======================
    # FOLLOW LINKS
    # =======================
    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True, svg_icon__isnull=False, url__isnull=False)
        .exclude(url="")
        .order_by("display_order")
    )

    # =======================
    # MAIN BANNER
    # =======================
    main_banner = MainBanner.objects.filter(
        status="published"
    ).first()

    # =======================
    # SITE INFO
    # =======================
    site_info = SiteMainInfo.objects.first()

    # =======================
    # HOME MEDIA
    # =======================
    home_medias = (
        Media.objects
        .filter(
            status="published",
            is_special=True,
        )
        .prefetch_related("images", "videos")
        .order_by("order")
    )

    # =======================
    # CONTEXT
    # =======================
    context = {
        "banners": banners,
        "active_slider": active_slider,
        "blogs": blogs,
        "special_products": special_products,
        "special_product_banners": special_product_banners,
        "categories": categories,
        "active_category": active_category,
        "statistics": statistics,
        "section": about_section,
        "group_companies": group_companies,
        "follow_links": follow_links,
        "site_info": site_info,
        "home_medias": home_medias,
        "main_banner": main_banner,
    }

    return render(request, "LTR/core/home.html", context)


def search(request):
    q = request.GET.get("q", "").strip()

    products = Product.objects.filter(
        Q(title_fa__icontains=q) |
        Q(title_en__icontains=q),
        status="published"
    )

    blogs = blog.objects.filter(
        Q(title_fa__icontains=q) |
        Q(title_en__icontains=q),
        status="published"
    )

    news = News.objects.filter(
        Q(title_fa__icontains=q) |
        Q(title_en__icontains=q),
        status="published"
    )

    context = {
        "query": q,
        "products": products,
        "blogs": blogs,
        "news": news,

        # داده‌های منو و فوتر
        "categories": (
            ProductCategory.objects
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__status="published")
                )
            )
            .filter(product_count__gt=0)
            .order_by("priority", "title_fa")
        ),
        "site_info": SiteMainInfo.objects.first(),
        "banner": OtherBanner.objects.filter(status="published").first(),
        "follow_links": (
            FollowUsLink.objects
            .filter(is_active=True, svg_icon__isnull=False)
            .exclude(url="")
            .order_by("display_order")
        ),
    }

    return render(
        request,
        "RTL/core/search.html",
        context
    )


# در انتهای app_core/views.py اضافه کن

from django.contrib.auth import authenticate, login as auth_login


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