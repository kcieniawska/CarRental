# Generated by Django 5.2 on 2025-04-17 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0003_car_is_recommended'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='rent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
