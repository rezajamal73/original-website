from django.urls import path
from app_hr.views import hr_home, hr_single

app_name = 'app_hr'

urlpatterns = [
    path('', hr_home, name='hr_home'),
    # صفحه جزئیات خبر
    path('<int:pid>/', hr_single, name='hr_single'),

]
