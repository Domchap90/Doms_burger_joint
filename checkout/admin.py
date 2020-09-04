from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_fee', 'order_total',
                       'grand_total')

    fields = ('order_number', 'date', 'name',
              'mobile_number', 'email',
              'address_line1', 'address_line2',
              'postcode', 'delivery_instructions',
              'delivery_fee', 'order_total', 'grand_total')

    list_display = ('order_number', 'date', 'name',
                    'order_total', 'delivery_fee',
                    'grand_total')

    ordering = ('-date',)


admin.site.register(Order, OrderAdmin)
