# Generated by Django 5.0.4 on 2024-08-12 05:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_alter_cartitem_cart'),
        ('product', '0007_rename_varient_price_productvariant_variant_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='product.productvariant'),
        ),
    ]