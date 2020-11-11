import uuid

from django.db import models
from django.core.validators import validate_email
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
    email = models.EmailField(max_length=80, null=False, blank=False, validators=[validate_email])
    mobile_number = models.CharField(max_length=15, null=False, blank=False)
    for_collection = models.BooleanField(default=False, null=True, blank=True, editable=True)
    # Postcode & address_line1 changed to required in the delivery form
    postcode = models.CharField(max_length=9, null=True, blank=True)
    address_line1 = models.CharField(max_length=80, null=True, blank=True)
    address_line2 = models.CharField(max_length=80, null=True, blank=True)
    delivery_instructions = models.CharField(max_length=100, null=True,
                                             blank=True)
    date = models.DateTimeField(auto_now_add=True)
    item_quantity_count = models.IntegerField(null=True, blank=True, default=0)
    combo_quantity_count = models.IntegerField(null=True, blank=True, default=0)
    order_count = models.IntegerField(null=False, blank=False, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2,
                                       null=False, default=0)
    discount = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0.00)
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
        self.item_quantity_count = self.lineitems.aggregate(Sum('quantity'))['quantity__sum']
        self.combo_quantity_count = self.lineitems.aggregate(Sum('combo_quantity'))['combo_quantity__sum']
        self.order_count = 0
        if self.item_quantity_count:
            self.order_count += self.item_quantity_count
        if self.combo_quantity_count:
            self.order_count += self.combo_quantity_count
        self.delivery_fee = settings.DELIVERY_FEE
        self.grand_total = float(self.order_total) + self.delivery_fee - float(self.discount)
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()

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
            self.lineitem_total = self.combo_item.price * self.combo_quantity
        else:
            self.lineitem_total = self.food_item.price * self.quantity

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
