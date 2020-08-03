from django.contrib import admin
from .models import Food_Item, Food_Category

# Register your models here.
admin.site.register(Food_Item)
admin.site.register(Food_Category)
