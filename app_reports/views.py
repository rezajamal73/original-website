from django.shortcuts import render
from app_banner.models import OtherBanner
from app_reports.models import CorporateSection, FollowUsLink, SiteMainInfo,DepartmentContact
from app_product.models import ProductCategory
from django.db.models import Count, Q
from app_reports.models import GroupCompany

# =====================================================
# COMMON CONTEXT
# =====================================================
def get_common_context():
    """
    داده‌های عمومی مشترک در تمام صفحات گزارش‌ها
    """
    site_info = SiteMainInfo.objects.first()

    follow_links = (
        FollowUsLink.objects
        .filter(is_active=True, svg_icon__isnull=False)
        .exclude(url="")
        .order_by("display_order")
    )

    banner = OtherBanner.objects.filter(status="published").first()

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
        .order_by("priority", "title_fa")),
        "site_info": site_info,
        "follow_links": follow_links,
        "banner": banner,
    }


# =====================================================
# GENERIC CORPORATE SECTION VIEW
# =====================================================
def corporate_section_view(request, section_type: str, template_name: str):
    section = (
        CorporateSection.objects
        .prefetch_related("texts__images", "texts__attachments")
        .filter(section_type=section_type, is_published=True)
        .first()
    )

    context = {
        **get_common_context(),
        "section": section,
    }

    return render(request, template_name, context)


# =====================================================
# VIEWS
# =====================================================
def vision_missions(request):
    return corporate_section_view(
        request,
        section_type="vision",
        template_name="RTL/reports/VM.html"
    )


def financial(request):
    return corporate_section_view(
        request,
        section_type="financial",
        template_name="RTL/reports/financial.html"
    )


def shareholder(request):
    return corporate_section_view(
        request,
        section_type="shareholder",
        template_name="RTL/reports/shareholder.html"
    )


def governance(request):
    return corporate_section_view(
        request,
        section_type="governance",
        template_name="RTL/reports/governance.html"
    )


def sustainability(request):
    return corporate_section_view(
        request,
        section_type="sustainability",
        template_name="RTL/reports/sustainability.html"
    )


def certificate(request):
    return corporate_section_view(
        request,
        section_type="certificate",
        template_name="RTL/reports/certificate.html"
    )



def department_contact_list(request):
    contacts = DepartmentContact.objects.all()
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
    context = {
        "categories": categories,
        "banner": banner,
        "follow_links": follow_links,
        "site_info": site_info,  # ✅ این خط کل مشکل را حل می‌کند
        "contacts": contacts,
    }

    return render(
        request,
        "RTL/reports/department.html",
        context
    )

def companies(request):
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

    group_companies = (
        GroupCompany.objects
        .filter(is_active=True, logo__isnull=False)
        .order_by("name")
    )

    context = {
        "categories": categories,
        "banner": banner,
        "site_info": site_info,
        "group_companies": group_companies,
    }

    return render(request, "RTL/reports/companies.html", context)
