# Generated by Django 5.2 on 2025-04-20 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0006_car_is_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='rental_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='rental_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
