from django.db import models
from django.conf import settings  # Importujemy settings, by uzyskać dostęp do modelu użytkownika
from django.contrib.auth.models import User
from datetime import date
    

# Model Equipment
class Equipment(models.Model):
    equipment = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.equipment

    
# Model Car
class Car(models.Model):
    CAR_CLASSES = [
        ("a", "małe i mini"),
        ("b", "miejskie"),
        ("c", "kompaktowe"),
        ("d", "rodzinne"),
        ("e", "limuzyny"),
        ("f", "luksusowe"),
        ("g", "sportowe"),
        ("h", "kabriolety"),
        ("i", "terenowe"),
        ("m", "van"),
    ]
    
    ENGINE_TYPES = [
        ('Diesel', 'Diesel'),
        ('Petrol', 'Benzyna'),
        ('Electric', 'Elektryczny'),
        ('Hybrid', 'Hybrydowy'),
    ]
    
    GEARBOX_TYPES = [
        ('Manual', 'Manualna'),
        ('Automatic', 'Automatyczna'),
    ]
    
    BODY_TYPES = [
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Kabriolet'),
        ('Wagon', 'Kombi'),
        ('Van', 'Van'),
        ('Pickup', 'Pickup'),
    ]
    
    category = models.CharField(max_length=50, choices=CAR_CLASSES)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = models.TextField(default="Nowoczesne, komfortowe i niezawodne auto, idealne do codziennych podróży oraz długich tras.")
    engine_type = models.CharField(max_length=10, choices=ENGINE_TYPES)  
    engine_capacity = models.PositiveSmallIntegerField()  
    engine_power = models.PositiveSmallIntegerField()  
    gearbox = models.CharField(max_length=10, choices=GEARBOX_TYPES)  
    fuel_consumption = models.DecimalField(max_digits=4, decimal_places=2)  
    image = models.ImageField(upload_to='car_images/')
    doors_count = models.PositiveSmallIntegerField()  
    seats_count = models.PositiveSmallIntegerField()  
    body_type = models.CharField(max_length=15, choices=BODY_TYPES)  
    year = models.PositiveSmallIntegerField()  
    location = models.CharField(max_length=100)  
    available = models.BooleanField(default=True)  
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    value = models.PositiveIntegerField()  
    mileage_limit = models.PositiveIntegerField()  
    equipment = models.ManyToManyField(Equipment)  # Relacja M:N do modelu Equipment
    is_recommended = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.brand} {self.model}"

    def update_average_rating(self):
        """Metoda do aktualizacji średniej oceny samochodu na podstawie opinii"""
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum([review.rating for review in reviews])
            self.average_rating = total_rating / len(reviews)
            self.save()
    def is_currently_available(self):
        today = date.today()
        return not self.orders.filter(start_date__lte=today, end_date__gte=today).exists()
    def set_availability(self):
        today = date.today()
        active_order = self.orders.filter(start_date__lte=today, end_date__gte=today).first()

        if active_order:
            self.is_available = False
            self.rental_start_date = active_order.start_date
            self.rental_end_date = active_order.end_date
        else:
            self.is_available = True
            self.rental_start_date = None
            self.rental_end_date = None
#Model opinii
class Review(models.Model):
    car = models.ForeignKey(Car, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)  # Używamy AUTH_USER_MODEL
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Opinia czeka na zatwierdzenie

    def __str__(self):
        return f"Opinia {self.user.username} o {self.car.brand} {self.car.model}"