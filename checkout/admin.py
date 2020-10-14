from django.contrib import admin
from .models import Order, OrderLineItem, ComboLineItem


class ComboLineItemInline(admin.StackedInline):
    model = ComboLineItem


class OrderLineItemAdmin(admin.ModelAdmin):
    inlines = (ComboLineItemInline,)


class OrderLineItemAdminInline(admin.TabularInline):
    """ Selected as an inline if the object instance is a combo """
    model = OrderLineItem
    fields = ("changeform_link", "food_item", "quantity", "combo_id",
              "combo_item", "combo_quantity", 'lineitem_total')

    readonly_fields = ('lineitem_total', 'changeform_link')

    list_display = ("changeform_link", "food_item", "quantity", "combo_id",
                    "combo_item", "combo_quantity", 'lineitem_total')


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_fee', 'order_total',
                       'grand_total', 'pid')

    fields = ('order_number', 'member_profile', 'date', 'name',
              'mobile_number', 'email',
              'address_line1', 'address_line2',
              'postcode', 'delivery_instructions',
              'delivery_fee', 'order_total', 'grand_total', 'pid')

    list_display = ('order_number', 'date', 'name',
                    'order_total', 'delivery_fee',
                    'grand_total')

    ordering = ('-date',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLineItem, OrderLineItemAdmin)
