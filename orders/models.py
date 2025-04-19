from django.db import models
from django.conf import settings
from cars.models import Car
from datetime import date
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    rental_days = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.car:
            raise ValueError("Cart must have a car assigned.")  # Upewniamy się, że car jest przypisany

        if self.start_date and self.end_date:
            rental_days = (self.end_date - self.start_date).days
            self.rental_days = rental_days
            self.total_price = self.car.rent * self.rental_days

        super(Cart, self).save(*args, **kwargs)
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
    
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
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

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            rental_days = (self.end_date - self.start_date).days
            self.rental_days = rental_days
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
            rental_days = (self.end_date - self.start_date).days
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
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.total_price = self.rental_days * self.price_per_day
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order Item for {self.car} ({self.rental_days} days)"

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User,AbstractUser, BaseUserManager  # Dodano import BaseUserManager
from django.db import models
from django.conf import settings
from cars.models import Car

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    objects = CustomUserManager()  # Użycie własnego menedżera

    def __str__(self):
        return self.username
    
class Review(models.Model):
    from django.conf import settings

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name='car_reviews', on_delete=models.CASCADE)
    rating = models.IntegerField() 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Opinia o {self.car} przez {self.user}"