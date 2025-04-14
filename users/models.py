from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager  # Dodano import BaseUserManager
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

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'W trakcie'),
        ('paid', 'Zapłacone'),
        ('completed', 'Zrealizowane'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_set')  # Unikalny related_name
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rental_days = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
