from django.db.models.signals import post_save, post_delete
from django.dispatch import django.receiver

from .models import OrderLineItem

post_save.connect(update_after_save)
post_delete.connect(update_after_delete)


def update_after_save(sender, instance, created, **kwargs):
    """ Update order total upon LineItem update """
    instance.order.update_total


def update_after_delete(sender, instance, **kwargs):
    """ Update order total upon LineItem update """
    instance.order.update_total
