from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Liczba dodatkowych pól do dodania w formularzu admina

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'city', 'payment_method', 'order_date', 'total_price']
    list_filter = ['payment_method', 'order_date']
    search_fields = ['first_name', 'last_name', 'email', 'city']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'car', 'rental_days', 'price_per_day', 'total_price']

