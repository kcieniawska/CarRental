from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Pole na nazwę wyposażenia

    def __str__(self):
        return self.name  # Powinno zwracać 'name', a nie 'equipment'


class Car(models.Model):
    ENGINE_TYPES = [
        ('Diesel', 'Diesel'),
        ('Petrol', 'Petrol'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ]
    
    GEARBOX_TYPES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic')
    ]
    
    BODY_TYPES = [
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Wagon', 'Wagon'),
        ('Van', 'Van'),
        ('Pickup', 'Pickup')
    ]
    
    CAR_CLASSES = [
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
    car_class = models.CharField(max_length=1, choices=CAR_CLASSES)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    engine_type = models.CharField(max_length=10, choices=ENGINE_TYPES)
    engine_capacity = models.PositiveSmallIntegerField()
    engine_power = models.PositiveSmallIntegerField()
    gearbox = models.CharField(max_length=10, choices=GEARBOX_TYPES)
    fuel_consumption = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.ImageField(upload_to="cars/")
    doors_count = models.PositiveSmallIntegerField()  # poprawiona literówka z "dors_count"
    seats_count = models.PositiveSmallIntegerField()
    body_type = models.CharField(max_length=15, choices=BODY_TYPES)
    year = models.PositiveSmallIntegerField()
    location = models.CharField(max_length=100)
    available = models.BooleanField(default=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.PositiveIntegerField()  # dodano brakujące nawiasy
    mileage_limit = models.PositiveIntegerField()
    equipment = models.ManyToManyField(Equipment)  # poprawiona nazwa modelu Equipment

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
