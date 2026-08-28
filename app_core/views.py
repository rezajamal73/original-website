import random

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from app_banner.models import (
    HeroBanner,
    OtherBanner,
    SpecialProductBanner,
    MainBanner,
    AboutBanner,
    HeroSliderSetting,
)

from app_blog.models import blog
from app_product.models import Product, ProductCategory

from app_reports.models import (
    CorporateSection,
    CorporateStatistic,
    GroupCompany,
)

from app_media.models import Media
from app_news.models import News
from app_seo.utils import SEOManager


# =====================================================
# CAPTCHA
# =====================================================

def _generate_captcha():
    return "".join(
        random.choice("0123456789")
        for _ in range(5)
    )


# =====================================================
# HOME
# =====================================================

def home(request, slug=None):

    # -------------------------------------------------
    # Detect language
    # -------------------------------------------------

    is_english = request.path.startswith("/en/")

    # -------------------------------------------------
    # Template
    # -------------------------------------------------

    template = (
        "LTR/core/home.html"
        if is_english
        else "RTL/core/home.html"
    )

    # -------------------------------------------------
    # Hero Banners
    # -------------------------------------------------

    banners = (
        HeroBanner.objects
        .filter(status="published")
        .order_by("order", "id")
    )

    # -------------------------------------------------
    # Hero Slider
    # -------------------------------------------------

    slider_setting = HeroSliderSetting.objects.first()

    active_slider = (
        slider_setting.active_slider
        if slider_setting
        else "hs_1"
    )

    # -------------------------------------------------
    # Blogs
    # -------------------------------------------------

    blogs = (
        blog.objects
        .filter(status="published")
        .order_by(
            "-publish_date_fa",
            "-publish_date_en"
        )[:3]
    )

    # -------------------------------------------------
    # Category
    # -------------------------------------------------

    active_category = None

    product_filter = Q(
        status="published"
    )

    if slug:

        active_category = get_object_or_404(
            ProductCategory,
            slug=slug
        )

        product_filter &= Q(
            category=active_category
        )

    # -------------------------------------------------
    # Special Products
    # -------------------------------------------------

    special_products = (
        Product.objects
        .filter(
            product_filter,
            special=True
        )
        .order_by(
            "priority",
            "title_fa"
        )[:12]
    )

    # -------------------------------------------------
    # Special Product Banners
    # -------------------------------------------------

    special_product_banners = (
        SpecialProductBanner.objects
        .filter(status="published")
        .order_by(
            "order",
            "created_at"
        )[:4]
    )

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    statistics = (
        CorporateStatistic.objects
        .filter(is_active=True)
        .order_by("display_order")
    )

    # -------------------------------------------------
    # About Section
    # -------------------------------------------------

    about_section = (
        CorporateSection.objects
        .filter(
            section_type="about",
            is_published=True
        )
        .prefetch_related(
            "texts",
            "about_items"
        )
        .select_related(
            "about_year"
        )
        .first()
    )

    # -------------------------------------------------
    # About Banner
    # -------------------------------------------------

    about_banner = (
        AboutBanner.objects
        .filter(status="published")
        .first()
    )

    # -------------------------------------------------
    # Group Companies
    # -------------------------------------------------

    group_companies = (
        GroupCompany.objects
        .filter(is_active=True)
        .order_by("display_order")
    )

    # -------------------------------------------------
    # Home Media
    # -------------------------------------------------

    home_medias = (
        Media.objects
        .filter(
            status="published",
            is_special=True
        )
        .prefetch_related(
            "images",
            "videos"
        )
        .order_by("order")
    )

    # -------------------------------------------------
    # Main Banner
    # -------------------------------------------------

    main_banner = (
        MainBanner.objects
        .filter(status="published")
        .first()
    )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    context = {

        "banners": banners,

        "about_banner": about_banner,

        "active_slider": active_slider,

        "blogs": blogs,

        "special_products": special_products,

        "special_product_banners": special_product_banners,

        "active_category": active_category,

        "statistics": statistics,

        "section": about_section,

        "group_companies": group_companies,

        "home_medias": home_medias,

        "main_banner": main_banner,

        "seo": SEOManager.get_page("home"),

        # Language
        "is_english": is_english,

    }

    return render(
        request,
        template,
        context
    )


# =====================================================
# ABOUT
# =====================================================

def about(request):

    is_english = request.path.startswith("/en/")

    template = (
        "LTR/core/history.html"
        if is_english
        else "RTL/core/history.html"
    )

    section = (
        CorporateSection.objects
        .filter(
            section_type="history",
            is_published=True
        )
        .prefetch_related(
            "texts__attachments"
        )
        .first()
    )

    context = {

        "section": section,

        "banner": (
            OtherBanner.objects
            .filter(status="published")
            .first()
        ),

        "seo": SEOManager.get_page("about"),

        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    is_english = request.path.startswith("/en/")

    template = (
        "LTR/core/contact.html"
        if is_english
        else "RTL/core/contact.html"
    )

    if "contact_captcha" not in request.session:

        request.session["contact_captcha"] = (
            _generate_captcha()
        )

    context = {

        "captcha_code": (
            request.session["contact_captcha"]
        ),

        "seo": SEOManager.get_page("contact"),

        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


# =====================================================
# CONTACT SECURITY
# =====================================================

def contact_security(request):

    is_english = request.path.startswith("/en/")

    template = (
        "LTR/core/contact_security.html"
        if is_english
        else "RTL/core/contact_security.html"
    )

    if "security_captcha" not in request.session:

        request.session["security_captcha"] = (
            _generate_captcha()
        )

    context = {

        "captcha_code": (
            request.session["security_captcha"]
        ),

        "seo": SEOManager.get_page(
            "contact_security"
        ),

        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


# =====================================================
# 404
# =====================================================

def error(request):

    is_english = request.path.startswith("/en/")

    template = (
        "LTR/core/404.html"
        if is_english
        else "RTL/core/404.html"
    )

    return render(
        request,
        template,
        {
            "seo": SEOManager.get_page("404"),
            "is_english": is_english,
        }
    )


# =====================================================
# SEARCH
# =====================================================

def search(request):

    is_english = request.path.startswith("/en/")

    template = (
        "LTR/core/search.html"
        if is_english
        else "RTL/core/search.html"
    )

    q = request.GET.get(
        "q",
        ""
    ).strip()

    context = {

        "query": q,

        # -------------------------------------------------
        # Products
        # -------------------------------------------------

        "products": Product.objects.filter(
            (
                Q(title_fa__icontains=q)
                |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),

        # -------------------------------------------------
        # Blogs
        # -------------------------------------------------

        "blogs": blog.objects.filter(
            (
                Q(title_fa__icontains=q)
                |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),

        # -------------------------------------------------
        # News
        # -------------------------------------------------

        "news": News.objects.filter(
            (
                Q(title_fa__icontains=q)
                |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),

        # -------------------------------------------------
        # SEO
        # -------------------------------------------------

        "seo": SEOManager.get_page("search"),

        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )