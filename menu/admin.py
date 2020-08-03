from django.contrib import admin
from .models import Food_Item, Food_Category

# Register your models here.


class Food_ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'price',
        'category',
        'order_quantity',
        'image',
    )

    ordering = ('order_quantity', 'category')


class Food_CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'friendly_name',
    )


admin.site.register(Food_Item, Food_ItemAdmin)
admin.site.register(Food_Category, Food_CategoryAdmin)
