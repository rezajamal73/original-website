from django.urls import path
from app_news.views import news_home, news_single, news_tag, news_category

app_name = 'app_news'

urlpatterns = [
    path('', news_home, name='news_home'),

    # فیلتر دسته‌بندی
    path('category/<slug:slug>/', news_category, name='news_category'),

    # صفحه جزئیات خبر
    path('<int:pid>/', news_single, name='news_single'),

    # فیلتر تگ
    path('tag/<slug:slug>/', news_tag, name='news_tag'),
]
