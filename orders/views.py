from django.db import models
from django.conf import settings
from cars.models import Car
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

# Widok koszyka
@login_required
def cart(request):
    # Pobieramy wszystkie przedmioty w koszyku
    cart_items = request.session.get('cart', [])
    
    # Obliczanie łącznej ceny koszyka
    total_price = sum(item['total_price'] for item in cart_items)
    
    return render(request, 'orders/cart.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Dodawanie do koszyka
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Pobierz liczbę dni z formularza POST
    rental_days = int(request.POST.get('rental_days', 1))

    # Pobieramy koszyk z sesji
    cart = request.session.get('cart', [])

    # Upewniamy się, że koszyk to lista
    if not isinstance(cart, list):
        cart = []

    # Sprawdź, czy samochód już jest w koszyku
    found = False
    for item in cart:
        if item.get('car_id') == car_id:
            item['rental_days'] += rental_days  # Dodajemy dni
            found = True
            break

    if not found:
        cart.append({
            'car_id': car.id,
            'rental_days': rental_days
        })

    # Zapisz koszyk
    request.session['cart'] = cart

    # Wiadomość z potwierdzeniem
    messages.success(
        request,
        f"Samochód <strong>{car.brand} {car.model}</strong> został dodany do koszyka na {rental_days} dzień/dni wynajmu :)"
    )

    return redirect('car_detail', car_id=car.id)
# Tworzenie zamówienia
@login_required
def checkout(request):
    cart = request.session.get('cart', [])

    # Jeśli koszyk jest pusty, wyświetlamy komunikat
    if not cart:
        return redirect('orders:cart')

    cleaned_cart = []
    total_price = Decimal('0.00')

    # Zbieramy dane zamówionych samochodów
    for item in cart:
        if 'rental_days' not in item:
            item['rental_days'] = 1  # Jeśli nie ma dni wynajmu, ustawiamy domyślnie 1 dzień

        try:
            car = Car.objects.get(id=item['car_id'])
            item['total_price'] = car.rent * item['rental_days']
            item['car_brand'] = car.brand
            item['car_model'] = car.model
            item['car_image'] = car.image.url if car.image else None
            cleaned_cart.append(item)
            total_price += item['total_price']
        except Car.DoesNotExist:
            continue

    # Obsługa formularza
    order_success = False
    if request.method == 'POST':
        # Możemy tutaj stworzyć zamówienie
        # Order.objects.create(user=request.user, total_price=total_price, items=cleaned_cart)
        
        # Opróżniamy koszyk po złożeniu zamówienia
        request.session['cart'] = []
        order_success = True

    return render(request, 'orders/checkout.html.jinja', {
        'cart_items': cleaned_cart,
        'total_price': total_price,
        'order_success': order_success,  # Przekazujemy zmienną do szablonu
    })

# Widok kart
@login_required
def cart_view(request):
    cart = request.session.get('cart', [])
    
    if not cart:
        return render(request, 'orders/cart.html.jinja', {
            'message': 'Twój koszyk jest pusty.'
        })

    cart_items = []
    total_price = 0

    for item in cart:
        if isinstance(item, dict):
            try:
                car = Car.objects.get(id=item['car_id'])
                rental_days = item.get('rental_days', 1)
                total_price += car.rent * rental_days

                cart_items.append({
                    'car_id': car.id,
                    'car_brand': car.brand,
                    'car_model': car.model,
                    'car_image': car.image.url if car.image else None,
                    'rental_days': rental_days,
                    'total_price': car.rent * rental_days,
                })
            except Car.DoesNotExist:
                continue

    return render(request, 'orders/cart.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

# Zaktualizowanie dni wynajmu
@login_required
def update_rental_days(request, car_id):
    cart = request.session.get('cart', [])
    
    for item in cart:
        if item['car_id'] == car_id:
            rental_days = int(request.POST.get('rental_days', 1))
            item['rental_days'] = rental_days
            try:
                car = Car.objects.get(id=car_id)
                item['total_price'] = float(car.rent * rental_days)
            except Car.DoesNotExist:
                continue
            break
    
    request.session['cart'] = cart
    return redirect('orders:cart')

# Usuwanie z koszyka
@login_required
def remove_from_cart(request, car_id):
    cart = request.session.get('cart', [])
    
    cart = [item for item in cart if item['car_id'] != car_id]
    
    request.session['cart'] = cart
    return redirect('orders:cart')

# Potwierdzenie
def confirmation(request):
    return render(request, 'orders/confirmation.html.jinja')
def order_confirmation(request):
    return render(request, 'orders/order_confirmation.html')