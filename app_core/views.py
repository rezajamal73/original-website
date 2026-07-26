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
    return "".join(random.choice("0123456789") for _ in range(5))


# =====================================================
# HOME
# =====================================================
def home(request, slug=None):

    banners = (
        HeroBanner.objects
        .filter(status="published")
        .order_by("order", "id")
    )

    slider_setting = HeroSliderSetting.objects.first()

    active_slider = (
        slider_setting.active_slider
        if slider_setting else "hs_1"
    )

    blogs = (
        blog.objects
        .filter(status="published")
        .order_by("-publish_date_fa", "-publish_date_en")[:3]
    )


    active_category = None
    product_filter = Q(status="published")

    if slug:
        active_category = get_object_or_404(
            ProductCategory,
            slug=slug
        )
        product_filter &= Q(category=active_category)


    special_products = (
        Product.objects
        .filter(product_filter, special=True)
        .order_by("priority", "title_fa")[:12]
    )


    special_product_banners = (
        SpecialProductBanner.objects
        .filter(status="published")
        .order_by("order", "created_at")[:4]
    )


    statistics = (
        CorporateStatistic.objects
        .filter(is_active=True)
        .order_by("display_order")
    )


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


    about_banner = (
        AboutBanner.objects
        .filter(status="published")
        .first()
    )


    group_companies = (
        GroupCompany.objects
        .filter(is_active=True)
        .order_by("display_order")
    )


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
        "main_banner": MainBanner.objects.filter(
            status="published"
        ).first(),
        "seo": SEOManager.get_page("home"),
    }


    return render(
        request,
        "RTL/core/home.html",
        context
    )



# =====================================================
# ABOUT
# =====================================================
def about(request):

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
        "banner": OtherBanner.objects.filter(
            status="published"
        ).first(),
        "seo": SEOManager.get_page("about"),
    }


    return render(
        request,
        "RTL/core/history.html",
        context
    )



# =====================================================
# CONTACT
# =====================================================
def contact(request):

    if "contact_captcha" not in request.session:
        request.session["contact_captcha"] = _generate_captcha()


    context = {
        "captcha_code": request.session["contact_captcha"],
        "seo": SEOManager.get_page("contact"),
    }


    return render(
        request,
        "RTL/core/contact.html",
        context
    )



# =====================================================
# CONTACT SECURITY
# =====================================================
def contact_security(request):

    if "security_captcha" not in request.session:
        request.session["security_captcha"] = _generate_captcha()


    context = {
        "captcha_code": request.session["security_captcha"],
        "seo": SEOManager.get_page(
            "contact_security"
        ),
    }


    return render(
        request,
        "RTL/core/contact_security.html",
        context
    )



# =====================================================
# 404
# =====================================================
def error(request):

    return render(
        request,
        "../templates/404.html",
        {
            "seo": SEOManager.get_page("404")
        }
    )



# =====================================================
# HOME EN
# =====================================================
def home_en(request, slug=None):

    context = home(request, slug).context_data

    return render(
        request,
        "LTR/core/home.html",
        context
    )



# =====================================================
# SEARCH
# =====================================================
def search(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()


    context = {

        "query": q,

        "products": Product.objects.filter(
            (
                Q(title_fa__icontains=q) |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),


        "blogs": blog.objects.filter(
            (
                Q(title_fa__icontains=q) |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),


        "news": News.objects.filter(
            (
                Q(title_fa__icontains=q) |
                Q(title_en__icontains=q)
            ),
            status="published"
        ),


        "seo": SEOManager.get_page(
            "search"
        ),
    }


    return render(
        request,
        "RTL/core/search.html",
        context
    )