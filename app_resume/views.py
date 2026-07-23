from django.shortcuts import render
from django.db.models import Count, Q

from .models import Resume
from app_product.models import ProductCategory
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo


def get_common_context():
    """
    داده‌های مشترک صفحات
    """
    return {
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


def resume_home(request):
    # ترتیب نمایش مطابق Drag & Drop در ادمین
    resumes = (
        Resume.objects
        .select_related("province")
        .order_by("display_order")
    )

    context = {
        "resumes": resumes,
        **get_common_context(),
    }

    return render(request, "RTL/resume/resume.html", context)