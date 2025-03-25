from django.db import models

class equipment(models.Model):
    equipment = models.CharField(max_length=50)
    def __str__(self):
        return self.equipment

class Car(models.Model):
    engine_types = [
        ('Diesel', 'Petrol', 'Electric', 'Hybrid')
    ]
    gearbox_types = [
        ('Manual', 'Automatic')
    ]
    body_types = [
        ('Sedan', 'Hatchback', 'SUV', 'Coupe', 'Convertible', 'Wagon', 'Van', 'Pickup')
    ]
    car_class = [
        ('A', 'małe auta miejskie'),
        ('B', 'auta miejskie'),
        ('C', 'kompaktowe'),
        ('D', 'średnie'),
        ('E', 'wyższe klasy'),
        ('F', 'luksusowe'),
        ('J', 'SUV-y'),
        ('M', 'vany'),
        ('S', 'sportowe'),
        ('T', 'pickup-y')
    ]
    car_class = models.CharField(max_length=1, choices=car_class)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    engine_type = models.CharField(max_length=50, choices=engine_types)
    engine_capacity = models.PositiveSmallIntegerField()
    engine_power = models.PositiveSmallIntegerField()
    gearbox = models.CharField(max_length=50, choices=gearbox_types)
    fuel_consumption = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.ImageField(upload_to="cars/")
    dors_count = models.PositiveSmallIntegerField()
    seats_count = models.PositiveSmallIntegerField()
    body_type = models.CharField(max_length=50, choices=body_types)
    year = models.PositiveSmallIntegerField()
    location = models.CharField(max_length=100)
    available = models.BooleanField(default=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.PositiveIntegerField
    mileage_limit = models.PositiveIntegerField()
    equipment = models.ManyToManyField(equipment)

    def __str__(self):
        return self.name