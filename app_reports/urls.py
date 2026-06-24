from django.urls import path
from .views import (
    vision_missions,
    financial,
    shareholder,
    governance,
    sustainability,
    certificate, department_contact_list,
    companies
)

app_name = "app_reports"

urlpatterns = [
    path("vision-missions/", vision_missions, name="vision_missions"),
    path("financial/", financial, name="financial"),
    path("shareholder/", shareholder, name="shareholder"),
    path("governance/", governance, name="governance"),
    path("sustainability/", sustainability, name="sustainability"),
    path("certificate/", certificate, name="certificate"),
    path("departments/", department_contact_list, name="department_contact_list"),
    path("companies/", companies, name="companies"),
]
