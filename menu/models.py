from django.db import models

# Create your models here.


class Food_Category (models.Model):
    name = models.CharField(max_length=20)
    friendly_name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name
 
    def get_friendly_name(self):
        return self.friendly_name


class Food_Item (models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    category = models.ForeignKey('Food_Category', null=True, blank=True, 
                                 on_delete=models.SET_NULL)
    order_quantity = models.IntegerField()
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name