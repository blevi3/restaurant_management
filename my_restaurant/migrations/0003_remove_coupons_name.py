# Generated by Django 3.0.14 on 2023-09-03 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_restaurant', '0002_cart_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupons',
            name='name',
        ),
    ]
