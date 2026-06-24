# app_tender/urls.py
from django.urls import path
from app_tender.views import *

app_name = "app_tender"

urlpatterns = [
    path('', tender_home, name='tender_home'),
    path('category/<str:cat_name>/', tender_home, name='tender_category'),
    path('<int:pid>/', tender_single, name='tender_single'),
    path('search/', tender_search, name='search'),
    path('tag/<slug:slug>/', tender_tag, name='tender_tag'),
]
