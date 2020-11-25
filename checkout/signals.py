from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem, ComboLineItem
from menu.models import Food_Item


@receiver(post_save, sender=OrderLineItem)
def update_orderline_after_save_lineitem(sender, instance, created, **kwargs):
    """ Update order total upon LineItem update """

    if instance.food_item:
        # Update the total purchased for food item
        food_item = Food_Item.objects.get(id=instance.food_item.id)
        food_item.total_purchased += instance.quantity
        food_item.save()

    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_orderline_after_delete(sender, instance, **kwargs):
    """ Update order total upon LineItem update & total purchased for each
    Food item """

    if instance.food_item:
        food_item = Food_Item.objects.get(id=instance.food_item.id)
        food_item.total_purchased -= instance.quantity
        food_item.save()

    instance.order.update_total()


@receiver(post_save, sender=ComboLineItem)
def update_comboline_after_save(sender, instance, created, **kwargs):
    """ Updates total purchased for each Food item upon saving combo
    orderline items"""

    food_item = Food_Item.objects.get(id=instance.food_item.id)
    food_item.total_purchased += (
        instance.quantity * instance.combo.combo_quantity)
    food_item.save()


@receiver(post_delete, sender=ComboLineItem)
def update_comboline_after_delete(sender, instance, **kwargs):
    """ Updates total purchased for each Food item upon deletion of combo
    orderline items"""

    food_item = Food_Item.objects.get(id=instance.food_item.id)
    food_item.total_purchased -= (
        instance.quantity * instance.combo.combo_quantity)
    food_item.save()
