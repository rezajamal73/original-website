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

app_name = "app_reports_en"

urlpatterns = [

    # =====================================================
    # ENGLISH  (prefix: /en/reports/ از urls.py اصلی میاد)
    # =====================================================

    path("vision-missions/", vision_missions, name="vision_missions_en"),
    path("financial/", financial, name="financial_en"),
    path("shareholder/", shareholder, name="shareholder_en"),
    path("governance/", governance, name="governance_en"),
    path("sustainability/", sustainability, name="sustainability_en"),
    path("certificate/", certificate, name="certificate_en"),
    path("departments/", department_contact_list, name="department_contact_list_en"),
    path("companies/", companies, name="companies_en"),
]