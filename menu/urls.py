from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('combo/', views.combo, name='combo'),
    path('sort/', views.sort_items,
         name="sort_items"),
    path('combo/item/', views.get_item,
         name="get_item"),
]
