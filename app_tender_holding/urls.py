from django.urls import path
from app_tender_holding.views import *

app_name = "app_tender_holding"

urlpatterns = [
    path('', tender_holding_home, name='tender_holding_home'),
    path('category/<str:cat_name>/', tender_holding_home, name='tender_holding_category'),
    path('<int:pid>/', tender_holding_single, name='tender_holding_single'),
    path('search/', tender_holding_search, name='search'),
    path('tag/<slug:slug>/', tender_holding_tag, name='tender_holding_tag'),
]
