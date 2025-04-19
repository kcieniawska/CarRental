from django.db import models
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.core.mail import send_mail
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import Cart, Order, CartItem, OrderItem
from cars.models import Car
from .forms import OrderForm
from django.views.decorators.http import require_POST


# === Pomocnicze ===
def calculate_total_price(order):
    total_price = 0
    for item in OrderItem.objects.filter(order=order):
        total_price += item.car.rent * item.rental_days
    return total_price

# === Widok koszyka (bazujący na bazie danych) ===

def clear_session_data(request):
    for key in [
        'car_brand', 'car_model', 'start_date', 'end_date', 'total_price',
        'first_name', 'last_name', 'email', 'phone_number', 'birth_date',
        'city', 'street', 'house_number', 'apartment_number', 'postal_code',
        'payment_method']:
        request.session.pop(key, None)


# === Widok koszyka ===
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cars:all_cars')

    total_price = sum(item.total_price for item in cart_items)

    first_item = cart_items.first()
    request.session['car_brand'] = first_item.car.brand
    request.session['car_model'] = first_item.car.model
    request.session['start_date'] = first_item.start_date.strftime('%Y-%m-%d')
    request.session['end_date'] = first_item.end_date.strftime('%Y-%m-%d')
    request.session['total_price'] = f"{total_price:.2f}"

    return render(request, 'orders/cart.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return redirect('cart')


# === Dodawanie samochodu do koszyka ===
@login_required
def car_detail(request, car_id):
    car = Car.objects.get(id=car_id)
    
    # Dodaj dzisiejszą datę do kontekstu
    context = {
        'car': car,
        'today': date.today(),  # Dzisiejsza data
        'default_end_date': date.today() + timedelta(days=1),  # Domyślna data końcowa
    }
    
    return render(request, 'cars/car.html.jinja', context)

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'cars/car.html.jinja', {
        'car': car,
        'today': date.today(),
        'default_end_date': date.today() + timedelta(days=1),
    })


@login_required
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not start_date or not end_date:
            messages.error(request, "Podaj daty wynajmu.")
            return redirect('cars:car_detail', car_id=car.id)

        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        rental_days = (end - start).days

        if rental_days <= 0:
            messages.error(request, "Data zakończenia musi być późniejsza.")
            return redirect('cars:car_detail', car_id=car.id)

        CartItem.objects.create(
            user=request.user,
            car=car,
            start_date=start,
            end_date=end,
            rental_days=rental_days,
            total_price=car.rent * rental_days
        )

        messages.success(request, f"Dodano {car.brand} {car.model} do koszyka.")
        return redirect('orders:cart')

    return redirect('cars:car_detail', car_id=car.id)
# === Checkout - formularz danych i przejście do płatności ===

# === Checkout ===
@login_required
def checkout(request):
    required_fields = ['car_brand', 'car_model', 'start_date', 'end_date', 'total_price']
    if not all(request.session.get(field) for field in required_fields):
        messages.error(request, "Wypełnij dane wynajmu.")
        return redirect('orders:cart')

    if request.method == 'POST':
        for field in ['first_name', 'last_name', 'email', 'phone_number', 'birth_date',
                      'city', 'street', 'house_number', 'apartment_number', 'postal_code', 'payment_method']:
            request.session[field] = request.POST.get(field)
        return redirect('orders:summary')

    return render(request, 'orders/checkout.html.jinja', {
        'car_brand': request.session.get('car_brand'),
        'car_model': request.session.get('car_model'),
        'start_date': request.session.get('start_date'),
        'end_date': request.session.get('end_date'),
        'total_price': request.session.get('total_price'),
    })


# === Summary ===
@login_required
def summary(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'orders/summary.html.jinja', {
        'cart_items': cart_items,
        **{key: request.session.get(key, f"Brak {key}") for key in [
            'first_name', 'last_name', 'email', 'phone_number', 'birth_date',
            'city', 'street', 'postal_code', 'house_number', 'apartment_number', 'payment_method']}
    })



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

# === Complete Order ===
@login_required
def complete_order(request):
    if request.method == 'POST':
        required_session_data = [
            'car_brand', 'car_model', 'start_date', 'end_date', 'total_price',
            'first_name', 'last_name', 'email', 'phone_number', 'birth_date',
            'city', 'street', 'house_number', 'apartment_number', 'postal_code', 'payment_method']

        if not all(key in request.session for key in required_session_data):
            messages.error(request, "Brakuje danych do złożenia zamówienia.")
            return redirect('orders:cart')

        try:
            car = Car.objects.get(brand=request.session['car_brand'], model=request.session['car_model'])
        except Car.DoesNotExist:
            messages.error(request, "Nie znaleziono samochodu.")
            return redirect('orders:cart')

        start_date = datetime.strptime(request.session['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.session['end_date'], '%Y-%m-%d').date()

        order = Order.objects.create(
            user=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_price=request.session['total_price'],
            first_name=request.session['first_name'],
            last_name=request.session['last_name'],
            email=request.session['email'],
            phone_number=request.session['phone_number'],
            birth_date=request.session['birth_date'],
            city=request.session['city'],
            street=request.session['street'],
            house_number=request.session['house_number'],
            apartment_number=request.session['apartment_number'],
            postal_code=request.session['postal_code'],
            payment_method=request.session['payment_method'],
        )

        clear_session_data(request)
        return redirect('orders:complete_order_success', order_id=order.id)

    return HttpResponse(status=405)


@login_required
def complete_order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/complete_order.html.jinja', {'order': order})


# === Widok profilu ===
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'users/profile.html.jinja', {'orders': orders})

def clear_session_data(request):
    # Usuwamy dane zamówienia z sesji
    del request.session['first_name']
    del request.session['last_name']
    del request.session['email']
    del request.session['phone_number']
    del request.session['birth_date']
    del request.session['city']
    del request.session['street']
    del request.session['house_number']
    del request.session['apartment_number']
    del request.session['postal_code']
    del request.session['payment_method']



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
def save_order_to_session(request, car, start_date, end_date, total_price, first_name, last_name, email, phone_number, birth_date, city, street, house_number, apartment_number, postal_code, payment_method):
    request.session['car_brand'] = car.brand
    request.session['car_model'] = car.model
    request.session['start_date'] = start_date
    request.session['end_date'] = end_date
    request.session['total_price'] = total_price
    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['email'] = email
    request.session['phone_number'] = phone_number
    request.session['birth_date'] = birth_date
    request.session['city'] = city
    request.session['street'] = street
    request.session['house_number'] = house_number
    request.session['apartment_number'] = apartment_number
    request.session['postal_code'] = postal_code
    request.session['payment_method'] = payment_method
# === Potwierdzenie zamówienia ===
from django.views.decorators.http import require_GET

@login_required
@require_GET
def order_confirmation(request, order_id):
    # Pobieramy zamówienie użytkownika lub 404
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Jeśli masz powiązane OrderItem, pobierz je — ale jeżeli nie używasz OrderItem, to usuń to
    order_items = getattr(order, 'items', None)
    if order_items:
        order_items = order.items.select_related('car').all()
        total_price = sum(item.total_price for item in order_items)
    else:
        order_items = []
        total_price = order.total_price  # fallback

    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
    }

    return render(request, 'orders/order_confirmation.html.jinja', context)


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
from django.views.decorators.http import require_POST


@login_required
def remove_from_cart(request, car_id):
    # Pobieramy przedmiot koszyka dla tego użytkownika i samochodu
    cart_item = CartItem.objects.filter(user=request.user, car_id=car_id).first()

    if cart_item:
        cart_item.delete()  # Usuwamy przedmiot

        # Możesz też dodać komunikat o sukcesie
        messages.success(request, f'Przedmiot "{cart_item.car.brand} {cart_item.car.model}" został usunięty z koszyka.')

    return redirect('orders:cart')  # Przekierowujemy z powrotem do koszyka


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
                # Tymczasowo usuwamy walidację dat
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
    # Pobierz koszyk z sesji
    cart_items = request.session.get('cart', [])
    
    # Oblicz całkowitą cenę
    total_price = sum(item['total_price'] for item in cart_items) if cart_items else 0
    
    return render(request, 'cart.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
# === Pomocnicza funkcja do tworzenia zamówienia z koszyka ===
