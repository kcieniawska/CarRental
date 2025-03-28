# Generated by Django 5.1.6 on 2025-03-25 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_class', models.CharField(choices=[('A', 'małe auta miejskie'), ('B', 'auta miejskie'), ('C', 'kompaktowe'), ('D', 'średnie'), ('E', 'wyższe klasy'), ('F', 'luksusowe'), ('J', 'SUV-y'), ('M', 'vany'), ('S', 'sportowe'), ('T', 'pickup-y')], max_length=1)),
                ('brand', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('engine_type', models.CharField(choices=[('Diesel', 'Diesel'), ('Petrol', 'Petrol'), ('Electric', 'Electric'), ('Hybrid', 'Hybrid')], max_length=10)),
                ('engine_capacity', models.PositiveSmallIntegerField()),
                ('engine_power', models.PositiveSmallIntegerField()),
                ('gearbox', models.CharField(choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')], max_length=10)),
                ('fuel_consumption', models.DecimalField(decimal_places=2, max_digits=4)),
                ('image', models.ImageField(upload_to='cars/')),
                ('doors_count', models.PositiveSmallIntegerField()),
                ('seats_count', models.PositiveSmallIntegerField()),
                ('body_type', models.CharField(choices=[('Sedan', 'Sedan'), ('Hatchback', 'Hatchback'), ('SUV', 'SUV'), ('Coupe', 'Coupe'), ('Convertible', 'Convertible'), ('Wagon', 'Wagon'), ('Van', 'Van'), ('Pickup', 'Pickup')], max_length=15)),
                ('year', models.PositiveSmallIntegerField()),
                ('location', models.CharField(max_length=100)),
                ('available', models.BooleanField(default=True)),
                ('rent', models.DecimalField(decimal_places=2, max_digits=10)),
                ('value', models.PositiveIntegerField()),
                ('mileage_limit', models.PositiveIntegerField()),
                ('equipment', models.ManyToManyField(to='cars.equipment')),
            ],
        ),
    ]
