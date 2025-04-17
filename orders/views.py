from django.db import models
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.core.mail import send_mail
from .models import Cart, Order, CartItem
from decimal import Decimal
from cars.models import Car
from .forms import OrderForm
from .models import Order, OrderItem, CartItem

def calculate_total_price(order):
    # Assuming you want to calculate the price based on rental days and the car's rent
    # Assuming there's a CartItem or OrderItem with the car and rental days for that order
    total_price = 0
    for item in OrderItem.objects.filter(order=order):  # Assuming you're using OrderItem
        total_price += item.car.rent * item.rental_days  # Car's rent per day multiplied by rental days
    return total_price
# === Widok koszyka (bazujący na bazie danych) ===

@login_required
def cart(request):
    cart = request.session.get('cart', [])
    updated_cart = []
    total_price = 0

    for item in cart:
        try:
            car = Car.objects.get(id=item['car_id'])

            # Konwertujemy daty z formatu string na datetime
            start_date = datetime.strptime(item.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(item.get('end_date'), '%Y-%m-%d')

            # Obliczamy liczbę dni wynajmu
            rental_days = (end_date - start_date).days

            # Jeśli liczba dni wynajmu jest mniejsza niż 1, ustawiamy ją na 1
            if rental_days < 1:
                rental_days = 1

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

# === Dodawanie samochodu do koszyka ===
@login_required
def add_to_cart(request, car_id):
    # Pobieramy samochód z bazy danych
    car = Car.objects.get(id=car_id)
    
    # Pobieramy daty z formularza
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    # Konwertujemy daty na datetime
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Obliczamy liczbę dni wynajmu
    rental_days = (end_date - start_date).days
    
    if rental_days <= 0:
        raise ValueError("Data zakończenia musi być późniejsza niż data rozpoczęcia.")
    
    # Konwertujemy daty na string w formacie YYYY-MM-DD
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Sprawdzamy, czy koszyk już istnieje w sesji
    cart = request.session.get('cart', [])
    
    # Obliczamy cenę i konwertujemy `Decimal` na `float`
    total_price = float(car.rent) * rental_days  # Zmieniamy na `float`
    
    # Dodajemy do koszyka
    cart.append({
        'car_id': car.id,
        'car_brand': car.brand,
        'car_model': car.model,
        'total_price': total_price,  # Wartość typu `float`
        'start_date': start_date_str,  # Przechowujemy daty jako string
        'end_date': end_date_str,
        'rental_days': rental_days,
    })
    
    # Zapisujemy koszyk w sesji
    request.session['cart'] = cart
    
    # Przekierowanie do koszyka
    return redirect('orders:cart')
# === Checkout - formularz danych i przejście do płatności ===

@login_required
def checkout(request):
    if request.method == 'POST':
        # Pobranie danych z formularza z użyciem `get()`
        request.session['first_name'] = request.POST.get('first_name', '')
        request.session['last_name'] = request.POST.get('last_name', '')
        request.session['birth_date'] = request.POST.get('birth_date', '')
        request.session['city'] = request.POST.get('city', '')
        request.session['street'] = request.POST.get('street', '')
        request.session['phone_number'] = request.POST.get('phone_number', '')
        request.session['postal_code'] = request.POST.get('postal_code', '')
        request.session['house_number'] = request.POST.get('house_number', '')
        request.session['apartment_number'] = request.POST.get('apartment_number', '')
        request.session['payment_method'] = request.POST.get('payment_method', '')

        # Jeśli wszystko jest w porządku, przekieruj na 'summary'
        return redirect('orders:summary')

    # Jeśli metoda to GET (pierwsze załadowanie strony), renderuj stronę checkout
    return render(request, 'orders/checkout.html.jinja')


def calculate_total_price_from_cart(cart):
    total_price = 0
    for item in cart:
        car = Car.objects.get(id=item['car_id'])
        total_price += car.rent * item['rental_days']  # Przykładowa kalkulacja
    return total_price

def calculate_total_price(order):
    # Tu możesz obliczyć cenę na podstawie samochodu i dat
    rental_days = (order.end_date - order.start_date).days
    return rental_days * order.car.rent  # Przykład kalkulacji

@login_required
def summary(request):
    # Pobranie danych z sesji
    first_name = request.session.get('first_name', '')
    last_name = request.session.get('last_name', '')
    birth_date = request.session.get('birth_date', '')
    city = request.session.get('city', '')
    street = request.session.get('street', '')
    phone_number = request.session.get('phone_number', '')
    postal_code = request.session.get('postal_code', '')
    house_number = request.session.get('house_number', '')
    apartment_number = request.session.get('apartment_number', '')
    payment_method = request.session.get('payment_method', '')
    total_price = request.session.get('total_price', 0)

    # Pobranie samochodów z sesji
    cars = request.session.get('cart', [])

    # Obliczenie całkowitej ceny (jeśli nie zapisano wcześniej)
    if not total_price:
        total_price = 0
        for item in cars:
            car = Car.objects.get(id=item['car_id'])
            rental_days = item.get('rental_days', 1)
            item_total_price = car.rent * rental_days
            total_price += item_total_price

    return render(request, 'orders/summary.html.jinja', {
        'first_name': first_name,
        'last_name': last_name,
        'birth_date': birth_date,
        'city': city,
        'street': street,
        'phone_number': phone_number,
        'postal_code': postal_code,
        'house_number': house_number,
        'apartment_number': apartment_number,
        'payment_method': payment_method,
        'cars': cars,
        'total_price': total_price,
    })
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
    cart = request.session.get('cart', [])

    if not isinstance(cart, list):  # Sprawdzamy, czy cart jest listą
        cart = []  # Jeśli nie, ustawiamy pustą listę

    # Usuwamy element z koszyka, który ma car_id równe przekazanemu car_id
    cart = [item for item in cart if item.get('car_id') != int(car_id)]

    # Zapisujemy zmieniony koszyk w sesji
    request.session['cart'] = cart

    return redirect('orders:cart')  # Przekierowanie do widoku koszyka


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
    # Pobranie cart z sesji, jeśli jest puste, to ustawiamy pusty słownik
    cart = request.session.get('cart', {})

    # Jeśli cart to lista, zmieńmy ją na słownik
    if isinstance(cart, list):
        cart = {str(idx): item for idx, item in enumerate(cart)}  # Tworzymy słownik z listy

    updated_cart = []
    total_price = 0

    # Iterowanie po elementach w cart
    for item in cart.values():
        try:
            # Pobranie danych samochodu z bazy
            car = Car.objects.get(id=item['car_id'])
            rental_days = item.get('rental_days', 1)  # Jeśli brak dni wynajmu, domyślnie 1
            item_total_price = car.rent * rental_days

            # Dodanie informacji o przedmiocie do listy
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

            # Sumowanie łącznej ceny
            total_price += item_total_price
        except Car.DoesNotExist:
            continue

    # Dodajemy dane samochodu do sesji (zaktualizowana wersja)
    if updated_cart:
        request.session['car_name'] = f"{updated_cart[0]['car_brand']} {updated_cart[0]['car_model']}"
        request.session['start_date'] = updated_cart[0]['start_date']
        request.session['end_date'] = updated_cart[0]['end_date']
        request.session['total_price'] = float(total_price)  # Konwersja Decimal do float

    return render(request, 'orders/cart.html.jinja', {
        'cart': updated_cart,
        'total_price': total_price,
    })

# === Pomocnicza funkcja do tworzenia zamówienia z koszyka ===

@login_required
def checkout_view(request):
    # Logika widoku dla checkout
    return render(request, 'orders/checkout.html.jinja')

@login_required
def complete_order(request):
    cart = request.session.get('cart', [])
    user = request.user

    if not cart:
        return redirect('orders:cart')  # jeśli koszyk pusty, przekieruj

    if request.method == 'POST':
        # Tworzymy formularz i zapisujemy dane do sesji
        form = OrderForm(request.POST)
        if form.is_valid():
            # Jeśli formularz jest poprawny, zapisujemy dane w sesji
            request.session['first_name'] = form.cleaned_data['first_name']
            request.session['last_name'] = form.cleaned_data['last_name']
            request.session['birth_date'] = form.cleaned_data['birth_date']
            request.session['email'] = form.cleaned_data['email']
            request.session['phone_number'] = form.cleaned_data['phone_number']
            request.session['street'] = form.cleaned_data['street']
            request.session['city'] = form.cleaned_data['city']
            request.session['postal_code'] = form.cleaned_data['postal_code']
            request.session['house_number'] = form.cleaned_data['house_number']
            request.session['apartment_number'] = form.cleaned_data['apartment_number']
            request.session['payment_method'] = form.cleaned_data['payment_method']

            total_price = 0  # Inicjalizujemy całkowitą cenę zamówienia

            # Tworzymy zamówienia
            for item in cart:
                car = Car.objects.get(id=item['car_id'])
                # Konwersja stringów na obiekty date
                start_date = datetime.strptime(item['start_date'], "%Y-%m-%d").date()
                end_date = datetime.strptime(item['end_date'], "%Y-%m-%d").date()

                order_item_price = car.rent * (end_date - start_date).days  # Kalkulacja ceny dla pozycji

                # Tworzymy zamówienie
                order = Order.objects.create(
                    user=user,
                    car=car,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=order_item_price,
                    payment_method=form.cleaned_data['payment_method'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    birth_date=form.cleaned_data['birth_date'],
                    city=form.cleaned_data['city'],
                    street=form.cleaned_data['street'],
                    postal_code=form.cleaned_data['postal_code'],
                    house_number=form.cleaned_data['house_number'],
                    apartment_number=form.cleaned_data['apartment_number'],
                    phone_number=form.cleaned_data['phone_number'],
                    order_date=datetime.now()  # Zapisujemy datę zamówienia (dzisiaj)
                )

                total_price += order_item_price  # Zbieramy całkowitą cenę za zamówienie

            # Zaktualizowanie całkowitej ceny zamówienia (zsumowana cena z wszystkich pozycji)
            order.total_price = total_price
            order.save()

            # Czyścimy koszyk po zapisaniu zamówienia
            request.session['cart'] = []

            return render(request, 'orders/order_complete.html.jinja', {'order': order})

    else:
        # Ustawiamy dane w formularzu, jeśli są dostępne w sesji
        initial_data = {
            'first_name': request.session.get('first_name', ''),
            'last_name': request.session.get('last_name', ''),
            'birth_date': request.session.get('birth_date', ''),
            'email': request.session.get('email', ''),
            'phone_number': request.session.get('phone_number', ''),
            'street': request.session.get('street', ''),
            'city': request.session.get('city', ''),
            'postal_code': request.session.get('postal_code', ''),
            'house_number': request.session.get('house_number', ''),
            'apartment_number': request.session.get('apartment_number', ''),
            'payment_method': request.session.get('payment_method', 'credit_card'),
        }

        form = OrderForm(initial=initial_data)

    return render(request, 'orders/complete_order.html.jinja', {'form': form})