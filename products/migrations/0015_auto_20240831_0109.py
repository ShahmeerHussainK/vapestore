# Generated by Django 3.2.14 on 2024-08-30 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0011_order_times_viewed'),
        ('reviews', '0005_alter_productreviews_product'),
        ('products', '0014_auto_20221124_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allproducts',
            name='sku',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='allproducts',
            name='slug',
            field=models.SlugField(blank=True, max_length=254, null=True),
        ),
        migrations.DeleteModel(
            name='NicotineShots',
        ),
    ]
