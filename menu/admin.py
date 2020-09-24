from django.contrib import admin
from .models import Food_Item, Food_Category, Food_Combo

# Register your models here.


class Food_ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'price',
        'category',
        'total_purchased',
        'image',
    )

    ordering = ('total_purchased', 'category')


class Food_ComboAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'price',
    )


class Food_CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'friendly_name',
    )


admin.site.register(Food_Item, Food_ItemAdmin)
admin.site.register(Food_Combo, Food_ComboAdmin)
admin.site.register(Food_Category, Food_CategoryAdmin)
# admin.site.register(Combo_Item, Combo_ItemAdmin)
