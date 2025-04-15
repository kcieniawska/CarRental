from django.db import models
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

from cars.models import Car
from .forms import OrderForm
from .models import Order, OrderItem, CartItem
from .cart import Cart

def calculate_total_price(order):
    total_price = 0

    # Dla każdego elementu zamówienia, obliczamy cenę na podstawie liczby dni wynajmu
    for order_item in order.orderitem_set.all():
        rental_days = order_item.rental_days
        car_price_per_day = order_item.car.rent  # Cena wynajmu na dzień
        total_price += rental_days * car_price_per_day  # Całkowity koszt

    # Zwróć łączną cenę
    return total_price
# === Widok koszyka (bazujący na bazie danych) ===
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)

    return render(request, 'orders/cart.html.jinja', {
        'cart': cart_items,
        'total_price': total_price,
    })


# === Dodawanie samochodu do koszyka ===
@login_required
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if not start_date or not end_date:
        messages.error(request, "Obie daty muszą być wybrane.")
        return redirect('car_detail', car_id=car.id)

    try:
        start_date_obj = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date_obj = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
    except ValueError:
        messages.error(request, "Niepoprawny format daty.")
        return redirect('car_detail', car_id=car.id)

    today = timezone.now()

    if end_date_obj <= start_date_obj:
        messages.error(request, "Data końcowa musi być późniejsza niż początkowa.")
        return redirect('car_detail', car_id=car.id)

    if start_date_obj < today:
        messages.error(request, "Data początkowa nie może być w przeszłości.")
        return redirect('car_detail', car_id=car.id)

    rental_days = (end_date_obj - start_date_obj).days
    total_price = float(car.rent * rental_days)

    cart = Cart(request)
    cart.add_item(car, rental_days, total_price, start_date_obj, end_date_obj)

    messages.success(request, f"Auto {car.brand} {car.model} dodane do koszyka! ({rental_days} dni)")
    return redirect('orders:cart')


# === Checkout - formularz danych i przejście do płatności ===

@login_required
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            # Tworzymy zamówienie, ale nie zapisujemy jeszcze do bazy danych
            order = form.save(commit=False)

            # Dodajemy ID samochodu i daty do zamówienia
            order.car = Car.objects.get(id=request.session['car_id'])
            order.start_date = request.session['start_date']
            order.end_date = request.session['end_date']

            # Jeśli masz pole użytkownika, przypisz go
            order.user = request.user
            order.total_price = calculate_total_price(order)  # Funkcja obliczająca cenę

            # Zapisujemy zamówienie
            order.save()

            # Zapisz ID zamówienia w sesji
            request.session['order_id'] = order.id

            # Przekierowanie do strony podsumowania
            return redirect('orders:summary')  # Przekierowanie na 'summary' po zapisaniu zamówienia
        else:
            # Jeśli formularz jest niepoprawny, zapisujemy dane w sesji, aby były dostępne przy kolejnym renderowaniu formularza
            request.session['first_name'] = request.POST.get('first_name')
            request.session['last_name'] = request.POST.get('last_name')
            request.session['email'] = request.POST.get('email')
            request.session['phone'] = request.POST.get('phone')
            request.session['street'] = request.POST.get('street')
            request.session['city'] = request.POST.get('city')
            request.session['postal_code'] = request.POST.get('postal_code')
            request.session['house_number'] = request.POST.get('house_number')

    else:
        # Przy pierwszym renderowaniu formularza, wypełniamy go danymi z sesji
        form = OrderForm(initial={
            'first_name': request.session.get('first_name', ''),
            'last_name': request.session.get('last_name', ''),
            'email': request.session.get('email', ''),
            'phone': request.session.get('phone', ''),
            'street': request.session.get('street', ''),
            'city': request.session.get('city', ''),
            'postal_code': request.session.get('postal_code', ''),
            'house_number': request.session.get('house_number', ''),
        })

    return render(request, 'orders/checkout.html.jinja', {'form': form})

@login_required
def summary(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('orders:checkout')  # Jeśli nie ma zamówienia w sesji, przekieruj do checkout

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('orders:checkout')  # Jeśli zamówienie nie istnieje, przekieruj do checkout

    return render(request, 'orders/summary.html.jinja', {'order': order})
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Załóżmy, że płatność jest zawsze udana
        order.payment_status = 'success'
        order.save()

        # Przekierowanie do strony potwierdzenia zamówienia
        return redirect('orders:order_confirmation', order_id=order.id)

    return render(request, 'orders/process_payment.html.jinja', {
        'order': order
    })
# === Potwierdzenie zamówienia ===
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_confirmation.html.jinja', {'order': order})

# === Zmiana liczby dni wynajmu ===
@login_required
def update_rental_days(request, car_id):
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(user=request.user, car_id=car_id)
            rental_days = int(request.POST.get('rental_days'))

            if rental_days >= 1:
                cart_item.rental_days = rental_days
                cart_item.total_price = cart_item.car.rent * rental_days
                cart_item.save()
                messages.success(request, f"Liczba dni wynajmu została zaktualizowana do {rental_days}.")
            else:
                messages.error(request, "Liczba dni wynajmu musi być co najmniej 1.")
        except CartItem.DoesNotExist:
            messages.error(request, "Nie znaleziono takiego elementu w koszyku.")
        return redirect('orders:cart')
    return HttpResponse(status=405)


# === Usuwanie z koszyka ===
@login_required
def remove_from_cart(request, car_id):
    cart = request.session.get('cart', {})
    cart = {k: v for k, v in cart.items() if v['car_id'] != car_id}
    request.session['cart'] = cart
    return redirect('orders:cart')


# === Widok potwierdzenia (statyczny) ===
def confirmation(request):
    return render(request, 'orders/confirmation.html.jinja')


# === Aktualizacja koszyka ===
@login_required
def update_cart(request):
    if request.method == 'POST':
        for item in CartItem.objects.filter(user=request.user):
            start_date = request.POST.get(f'start_date_{item.car_id}')
            end_date = request.POST.get(f'end_date_{item.car_id}')
            rental_days = int(request.POST.get(f'rental_days_{item.car_id}', 0))

            if start_date and end_date and rental_days > 0:
                item.start_date = start_date
                item.end_date = end_date
                item.rental_days = rental_days
                item.total_price = item.car.rent * rental_days
                item.save()

        return redirect('orders:cart')
    return HttpResponse(status=405)


# === Widok koszyka z sesji ===
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    updated_cart = []
    total_price = 0

    for item in cart.values():
        try:
            car = Car.objects.get(id=item['car_id'])
            rental_days = item.get('rental_days', 1)
            item_total_price = car.rent * rental_days

            updated_cart.append({
                'car_id': car.id,
                'car_brand': car.brand,
                'car_model': car.model,
                'rental_days': rental_days,
                'total_price': item_total_price,
                'car_image': car.image.url if car.image else None,
                'start_date': item.get('start_date'),
                'end_date': item.get('end_date')
            })

            total_price += item_total_price
        except Car.DoesNotExist:
            continue

    return render(request, 'orders/cart.html.jinja', {
        'cart': updated_cart,
        'total_price': total_price,
    })


# === Pomocnicza funkcja do tworzenia zamówienia z koszyka ===
def create_order_from_cart(request):
    cart = request.session.get('cart', {})
    if not cart:
        return None

    order = Order.objects.create(user=request.user, total_price=0)  # price uzupełnimy później

    for item in cart.values():
        car = get_object_or_404(Car, id=item['car_id'])
        OrderItem.objects.create(
            order=order,
            car=car,
            rental_days=item['rental_days'],
            total_price=item['total_price']
        )

    return order
