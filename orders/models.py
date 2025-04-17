from django.db import models
from django.conf import settings
from cars.models import Car
from django.utils import timezone
from datetime import date

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    rental_days = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            print(f"Start date: {self.start_date}, End date: {self.end_date}")
            rental_days = (self.end_date - self.start_date).days
            print(f"Calculated rental days: {rental_days}")
            if rental_days <= 0:
                raise ValueError("Data końcowa musi być późniejsza niż data początkowa.")
            self.rental_days = rental_days
            self.total_price = self.car.rent * self.rental_days
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return f"Cart for {self.user.username} from {self.start_date} to {self.end_date}"

class Order(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Karta kredytowa'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Przelew bankowy'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Zrealizowane'),
        ('in_progress', 'W trakcie'),
        ('not_completed', 'Niezrealizowane'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='orders')
    start_date = models.DateField()
    end_date = models.DateField()
    rental_days = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    street = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    house_number = models.CharField(max_length=20)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='credit_card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    order_date = models.DateTimeField(auto_now_add=True)  # Data zamówienia (dzisiaj)
    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            # Debugging: sprawdźmy, czy daty są prawidłowe
            print(f"Start date: {self.start_date}, End date: {self.end_date}")

            # Obliczamy różnicę w dniach wynajmu
            rental_days = (self.end_date - self.start_date).days

            # Debugging: sprawdźmy obliczoną liczbę dni
            print(f"Calculated rental days: {rental_days}")

            # Jeśli liczba dni wynajmu jest <= 0, zwrócimy błąd
            if rental_days <= 0:
                raise ValueError("Data końcowa musi być późniejsza niż data początkowa.")
            
            # Ustawiamy liczbę dni wynajmu
            self.rental_days = rental_days

            # Obliczamy cenę za wynajem
            self.total_price = self.car.rent * self.rental_days

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(default=timezone.localdate)
    rental_days = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            # Logowanie dat wejściowych
            print(f"Start date: {self.start_date}, End date: {self.end_date}")
            
            # Obliczanie dni wynajmu
            rental_days = (self.end_date - self.start_date).days
            print(f"Calculated rental days: {rental_days}")

            if rental_days <= 0:
                raise ValueError("Data końcowa musi być późniejsza niż data początkowa.")
            self.rental_days = rental_days
            self.total_price = self.car.rent * self.rental_days

        super(CartItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"Cart Item for {self.user.username} - {self.car.brand} {self.car.model}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rental_days = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.rental_days * self.price_per_day
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order Item for {self.car} ({self.rental_days} days)"