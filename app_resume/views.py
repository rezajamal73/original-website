
from django.shortcuts import render
from django.db.models import Count, Q

from .models import Resume
from app_product.models import ProductCategory
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo
from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English pages based on URL name.

    Persian:
        resume

    English:
        resume_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


# =====================================================
# COMMON CONTEXT
# =====================================================

def get_common_context():

    return {
        "categories": (
            ProductCategory.objects
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(
                        products__status="published"
                    )
                )
            )
            .filter(
                product_count__gt=0
            )
            .order_by(
                "priority",
                "title_fa"
            )
        ),

        "site_info": (
            SiteMainInfo.objects.first()
        ),

        "banner": (
            OtherBanner.objects
            .filter(
                status="published"
            )
            .first()
        ),

        "follow_links": (
            FollowUsLink.objects
            .filter(
                is_active=True,
                svg_icon__isnull=False
            )
            .exclude(
                url=""
            )
            .order_by(
                "display_order"
            )
        ),
    }


# =====================================================
# RESUME HOME
# =====================================================

def resume_home(request):

    is_english = is_english_request(request)

    resumes = (
        Resume.objects
        .select_related("province")
        .order_by("display_order")
    )

    seo = SEOManager.get_page("resume")

    template_name = (
        "LTR/resume/resume.html"
        if is_english
        else "RTL/resume/resume.html"
    )

    context = {
        **get_common_context(),

        "resumes": resumes,

        "seo": seo,

        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context,
    )

