from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('sort/', views.sort_items,
         name="sort_items"),
]
