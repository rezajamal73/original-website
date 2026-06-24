from django.urls import path
from app_auction.views import (
    auction_home,
    auction_single,
    auction_tag,
    auction_search,
)

app_name = "app_auction"

urlpatterns = [
    path('', auction_home, name='auction_home'),
    path('category/<str:cat_name>/', auction_home, name='auction_category'),
    path('<int:pid>/', auction_single, name='auction_single'),
    path('author/<str:author_username>/', auction_home, name='auction_author'),
    path('search/', auction_search, name='auction_search'),
    path('tag/<slug:slug>/', auction_tag, name='auction_tag'),
]
