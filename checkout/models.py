import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from menu.models import Food_Item


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    mobile_number = models.CharField(max_length=13, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    address_line1 = models.CharField(max_length=80, null=False, blank=False)
    address_line2 = models.CharField(max_length=80, null=True, blank=True)
    delivery_instructions = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.delivery_fee = settings.DELIVERY_FEE
        self.grand_total = float(self.order_total) + self.delivery_fee
        print(f'Update_total accessed. Order_total = {self.order_total}, delivery_fee = {self.delivery_fee}, grand_total = {self.grand_total}.')
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        print('save order accessed.')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    food_item = models.ForeignKey(Food_Item, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.food_item.price * self.quantity
        print('save orderlineitem accessed.')
        print(self.lineitem_total)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Item Id {self.food_item.pk} on order '
        '{self.order.order_number}'
