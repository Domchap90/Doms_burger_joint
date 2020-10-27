from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('check_postcode_home/', views.check_postcode_home, name='check_postcode_home'),
]
