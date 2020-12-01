from django.urls import path
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<order_number>', views.checkout_success,
         name='checkout_success'),
    path('collect_or_delivery/', views.collect_or_delivery,
         name='collect_or_delivery'),
    path('is_form_valid/<is_collect>/', views.is_form_valid,
         name='is_form_valid'),
    path('wh/', webhook, name="webhook"),
    path('cached_payment_intent/', views.cached_payment_intent,
         name='cached_payment_intent')
]
