from django.shortcuts import render

from app_reports.models import (
    CorporateSection,
    DepartmentContact,
    GroupCompany,
)

from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English pages based on URL name.

    Persian:
        vision_missions
        financial
        shareholder
        governance
        sustainability
        certificate
        department_contact_list
        companies

    English:
        vision_missions_en
        financial_en
        shareholder_en
        governance_en
        sustainability_en
        certificate_en
        department_contact_list_en
        companies_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


# =====================================================
# GENERIC CORPORATE SECTION VIEW
# =====================================================

def corporate_section_view(
    request,
    section_type: str,
    template_fa: str,
    template_en: str,
):

    is_english = is_english_request(request)

    template_name = (
        template_en
        if is_english
        else template_fa
    )

    section = (
        CorporateSection.objects
        .prefetch_related(
            "texts__images",
            "texts__attachments",
        )
        .filter(
            section_type=section_type,
            is_published=True,
        )
        .first()
    )

    context = {
        "section": section,
        "seo": SEOManager.get_page(section_type),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context,
    )


# =====================================================
# VISION & MISSIONS
# =====================================================

def vision_missions(request):

    return corporate_section_view(
        request,
        section_type="vision",
        template_fa="RTL/reports/VM.html",
        template_en="LTR/reports/VM.html",
    )


# =====================================================
# FINANCIAL
# =====================================================

def financial(request):

    return corporate_section_view(
        request,
        section_type="financial",
        template_fa="RTL/reports/financial.html",
        template_en="LTR/reports/financial.html",
    )


# =====================================================
# SHAREHOLDER
# =====================================================

def shareholder(request):

    return corporate_section_view(
        request,
        section_type="shareholder",
        template_fa="RTL/reports/shareholder.html",
        template_en="LTR/reports/shareholder.html",
    )


# =====================================================
# CORPORATE GOVERNANCE
# =====================================================

def governance(request):

    return corporate_section_view(
        request,
        section_type="governance",
        template_fa="RTL/reports/governance.html",
        template_en="LTR/reports/governance.html",
    )


# =====================================================
# SUSTAINABILITY
# =====================================================

def sustainability(request):

    return corporate_section_view(
        request,
        section_type="sustainability",
        template_fa="RTL/reports/sustainability.html",
        template_en="LTR/reports/sustainability.html",
    )


# =====================================================
# CERTIFICATE
# =====================================================

def certificate(request):

    return corporate_section_view(
        request,
        section_type="certificate",
        template_fa="RTL/reports/certificate.html",
        template_en="LTR/reports/certificate.html",
    )


# =====================================================
# DEPARTMENT CONTACTS
# =====================================================

def department_contact_list(request):

    is_english = is_english_request(request)

    template_name = (
        "LTR/reports/department.html"
        if is_english
        else "RTL/reports/department.html"
    )

    contacts = DepartmentContact.objects.all()

    context = {
        "contacts": contacts,
        "seo": SEOManager.get_page("department"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context,
    )


# =====================================================
# GROUP COMPANIES
# =====================================================

def companies(request):

    is_english = is_english_request(request)

    template_name = (
        "LTR/reports/companies.html"
        if is_english
        else "RTL/reports/companies.html"
    )

    group_companies = (
        GroupCompany.objects
        .filter(
            is_active=True,
            logo__isnull=False,
        )
        .order_by("name")
    )

    context = {
        "group_companies": group_companies,
        "seo": SEOManager.get_page("companies"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context,
    )