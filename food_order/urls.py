from django.urls import path
from . import views

urlpatterns = [
    path('', views.food_order, name='food_order'),
    path('add/<item_id>/', views.add_to_order, name='add_to_order'),
    path('remove/<item_id>/', views.remove_from_order, name='remove_from_order'),
    path('edit_item/<item_id>/', views.edit_order, name='edit_order'),
]
