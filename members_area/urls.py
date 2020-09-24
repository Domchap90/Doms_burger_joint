from django.urls import path
from . import views

urlpatterns = [
    path('', views.members_area, name='members_area'),
    path('rewards/', views.rewards, name='rewards'),
]
