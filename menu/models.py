from django.db import models

# Create your models here.


class Food_Category (models.Model):

    class Meta:
        verbose_name_plural = 'Food_Categories'
    name = models.CharField(max_length=20)
    friendly_name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name
 
    def get_friendly_name(self):
        return self.friendly_name


class Food_Combo (models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name


class Food_Item (models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    category = models.ForeignKey('Food_Category', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    total_purchased = models.IntegerField()
    image = models.ImageField(null=True, blank=True)
    food_combos = models.ManyToManyField(Food_Combo, related_name='food_items')

    def __str__(self):
        return self.name
