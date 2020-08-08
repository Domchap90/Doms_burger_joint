from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    # path('get/ajax/filter_results/', views.filter_results,
    #      name="filter"),
    path('sort/', views.sort_items,
         name="sort_items"),
]
