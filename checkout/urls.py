from django.urls import path
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<order_number>', views.checkout_success,
         name='checkout_success'),
    path('check_postcode', views.check_postcode, name='check_postcode'),
    path('wh/', webhook, name="webhook"),
    path('cached_payment_intent/', views.cached_payment_intent,
         name='cached_payment_intent')
]