from django.urls import path

from .views import (
    vision_missions,
    financial,
    shareholder,
    governance,
    sustainability,
    certificate,
    department_contact_list,
    companies,
)

app_name = "app_reports"


urlpatterns = [

    # =====================================================
    # PERSIAN
    # =====================================================

    path(
        "vision-missions/",
        vision_missions,
        name="vision_missions",
    ),

    path(
        "financial/",
        financial,
        name="financial",
    ),

    path(
        "shareholder/",
        shareholder,
        name="shareholder",
    ),

    path(
        "governance/",
        governance,
        name="governance",
    ),

    path(
        "sustainability/",
        sustainability,
        name="sustainability",
    ),

    path(
        "certificate/",
        certificate,
        name="certificate",
    ),

    path(
        "departments/",
        department_contact_list,
        name="department_contact_list",
    ),

    path(
        "companies/",
        companies,
        name="companies",
    ),


    # =====================================================
    # ENGLISH
    # =====================================================

    path(
        "en/vision-missions/",
        vision_missions,
        name="vision_missions_en",
    ),

    path(
        "en/financial/",
        financial,
        name="financial_en",
    ),

    path(
        "en/shareholder/",
        shareholder,
        name="shareholder_en",
    ),

    path(
        "en/governance/",
        governance,
        name="governance_en",
    ),

    path(
        "en/sustainability/",
        sustainability,
        name="sustainability_en",
    ),

    path(
        "en/certificate/",
        certificate,
        name="certificate_en",
    ),

    path(
        "en/departments/",
        department_contact_list,
        name="department_contact_list_en",
    ),

    path(
        "en/companies/",
        companies,
        name="companies_en",
    ),
]