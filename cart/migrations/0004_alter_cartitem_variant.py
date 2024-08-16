# Generated by Django 5.0.4 on 2024-08-12 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_cartitem_variant'),
        ('product', '0007_rename_varient_price_productvariant_variant_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productvariant'),
        ),
    ]