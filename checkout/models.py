import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from menu.models import Food_Item, Food_Combo
from members_area.models import MemberProfile


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    member_profile = models.ForeignKey(
                     MemberProfile, on_delete=models.SET_NULL, null=True,
                     blank=True, related_name='orders'
                     )
    name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    mobile_number = models.CharField(max_length=13, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    address_line1 = models.CharField(max_length=80, null=False, blank=False)
    address_line2 = models.CharField(max_length=80, null=True, blank=True)
    delivery_instructions = models.CharField(max_length=200, null=True,
                                             blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2,
                                       null=False, default=0)
    # discount = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, 
                                      null=False, default=0)
    pid = models.CharField(max_length=254, null=False, blank=False, default='')

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
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    food_item = models.ForeignKey(Food_Item, null=True, blank=True,
                                  on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    combo_item = models.ForeignKey(Food_Combo, null=True, blank=True,
                                   on_delete=models.CASCADE)
    combo_id = models.CharField(max_length=256, null=True, blank=True)
    combo_quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, null=False,
        blank=False, editable=False)

    def changeform_link(self):
        """
        Link to OrderLineItems own Model page allowing
        another inline link to be created for the ComboLineItems
        """
        if self.id:
            if self.combo_item:
                changeform_url = reverse(
                    'admin:checkout_orderlineitem_change', args=(self.id,)
                )
                return mark_safe(
                    '<a href="{link}" target="_blank">See Contents</a>'.format(
                        link=changeform_url
                    ))
            else:
                return self.food_item
        return ''
    changeform_link.allow_tags = True
    changeform_link.short_description = 'Items'

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        if self.combo_item:
            print(f'self.combo_item.price = {self.combo_item.price} is of type {type(self.combo_item.price)} \
                and self.combo_quantity = {self.combo_quantity} is of type {type(self.combo_quantity)}')
            self.lineitem_total = self.combo_item.price * self.combo_quantity
        else:
            self.lineitem_total = self.food_item.price * self.quantity
        print('save orderlineitem accessed.')
        print(self.lineitem_total)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.combo_item:
            return f'Combo Id {self.combo_item.pk} on order \
        {self.order.order_number}'
        else:
            return f'Item Id {self.food_item.pk} on order \
        {self.order.order_number}'


class ComboLineItem(models.Model):
    combo = models.ForeignKey(OrderLineItem, null=False, blank=False, on_delete=models.CASCADE, related_name='combocontents')
    food_item = models.ForeignKey(Food_Item, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)

    def save(self, *args, **kwargs):
        """
        Update the contents of the combo represented by the id.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Food item Id: {self.food_item.pk} added to combo \
        {self.combo.combo_id}'
