# Generated by Django 3.0.14 on 2023-09-03 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_restaurant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='discount',
            field=models.IntegerField(default=0),
        ),
    ]
