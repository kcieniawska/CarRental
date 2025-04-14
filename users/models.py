from django.contrib.auth import get_user_model  # Dodaj ten import
from django.contrib.auth.models import AbstractUser, BaseUserManager  # Brakujący import
from django.db import models
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
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Użycie get_user_model()
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rental_days = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    rental_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.car} by {self.user}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
