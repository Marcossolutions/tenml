# Generated by Django 5.0.4 on 2024-08-01 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0002_alter_category_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('product_decription', models.TextField(verbose_name=1000)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('offer_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('thumbnail', models.ImageField(null=True, upload_to='thumbnail_image')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('product_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='category.category')),
            ],
        ),
    ]