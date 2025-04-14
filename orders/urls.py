# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'  # Przestrzeń nazw

urlpatterns = [
    path('add_to_cart/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),  # jeśli masz widok koszyka
    path('remove_from_cart/<int:car_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('update_rental_days/<int:car_id>/', views.update_rental_days, name='update_rental_days'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation')
    
]
