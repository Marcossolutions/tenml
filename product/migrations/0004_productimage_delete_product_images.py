# Generated by Django 5.0.4 on 2024-08-01 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(default='E:\\Brototype\\ecom Project\\tenml\\static\\adminside\\assets\\imgs\\product_images\\No image.jpg', upload_to='product_images')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.product')),
            ],
        ),
        migrations.DeleteModel(
            name='Product_images',
        ),
    ]
