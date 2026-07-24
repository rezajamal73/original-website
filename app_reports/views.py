from django.shortcuts import render

from app_reports.models import (
    CorporateSection,
    DepartmentContact,
    GroupCompany,
)

from app_seo.utils import SEOManager



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
        "section": section,
        "seo": SEOManager.get_page(section_type),
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

    context = {
        "contacts": contacts,
        "seo": SEOManager.get_page("department"),
    }

    return render(
        request,
        "RTL/reports/department.html",
        context
    )
def companies(request):

    group_companies = (
        GroupCompany.objects
        .filter(is_active=True, logo__isnull=False)
        .order_by("name")
    )

    context = {
        "group_companies": group_companies,
        "seo": SEOManager.get_page("companies"),
    }

    return render(
        request,
        "RTL/reports/companies.html",
        context
    )