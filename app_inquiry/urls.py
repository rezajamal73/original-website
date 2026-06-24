from django.urls import path
from .views import (
    inquiry_home,
    inquiry_single,
    inquiry_tag,
    inquiry_search,
)

app_name = "app_inquiry"

urlpatterns = [
    path("", inquiry_home, name="home"),
    path("category/<slug:slug>/", inquiry_home, name="category"),
    path("<int:pk>/", inquiry_single, name="single"),
    path("tag/<slug:slug>/", inquiry_tag, name="tag"),
    path("search/", inquiry_search, name="search"),
]
