# Generated by Django 3.0.8 on 2020-10-13 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0006_order_order_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='combo_quantity_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='quantity_count',
            field=models.IntegerField(default=0),
        ),
    ]