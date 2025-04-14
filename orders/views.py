from .models import Order, Cart
from cars.models import Car
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
import json

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
    try:
        car = Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return redirect('index')  # Jeśli samochód nie istnieje, wracamy na stronę główną

    # Pobieramy koszyk z sesji
    cart = request.session.get('cart', [])

    # Upewnij się, że cart jest listą
    if not isinstance(cart, list):
        cart = []  # Inicjujemy pustą listę, jeśli koszyk nie jest listą

    # Debugowanie - sprawdzamy zawartość koszyka przed dodaniem
    print("Koszyk przed dodaniem:", cart)

    # Sprawdzamy, czy samochód jest już w koszyku
    found = False
    for item in cart:
        if isinstance(item, dict):  # Upewniamy się, że item jest słownikiem
            if item['car_id'] == car_id:
                item['rental_days'] += 1  # Zwiększamy dni wynajmu, jeśli samochód jest w koszyku
                found = True
                break
        else:
            print(f"Błąd: item {item} nie jest słownikiem!")
    
    # Jeśli samochód nie jest w koszyku, dodajemy go
    if not found:
        cart.append({
            'car_id': car.id,
            'rental_days': 1  # Domyślnie dodajemy 1 dzień wynajmu
        })

    # Zapisujemy zmodyfikowany koszyk w sesji
    request.session['cart'] = cart

    # Debugowanie - sprawdzamy zawartość koszyka po dodaniu
    print("Koszyk po dodaniu:", cart)

    return redirect('orders:cart')


# Tworzenie zamówienia
@login_required
def checkout(request):
    cart = request.session.get('cart', [])

    # Jeśli koszyk jest pusty, wyświetlamy komunikat
    if not cart:
        return redirect('orders:cart')

    # Zbieramy dane zamówionych samochodów
    cleaned_cart = []
    total_price = Decimal('0.00')

    for item in cart:
        if isinstance(item, dict):
            # Sprawdzamy, czy każdy przedmiot zawiera `rental_days`
            if 'rental_days' not in item:
                item['rental_days'] = 1  # Jeśli nie ma, ustawiamy domyślnie na 1
            try:
                car = Car.objects.get(id=item['car_id'])
                item['total_price'] = car.rent * item['rental_days']  # Obliczamy cenę
                item['car_brand'] = car.brand
                item['car_model'] = car.model
                item['car_image'] = car.image.url if car.image else None  # Sprawdzamy, czy zdjęcie jest dostępne

                cleaned_cart.append(item)
                total_price += item['total_price']  # Sumujemy do całkowitej ceny
            except Car.DoesNotExist:
                continue

    # Debugowanie: sprawdzenie danych w cleaned_cart
    print(cleaned_cart)

    # Po zatwierdzeniu zamówienia ustawiamy 'order_success' na True
    order_success = False
    if request.method == 'POST':
        # Logika do zatwierdzenia zamówienia (np. zapis w bazie danych)
        order_success = True
        # Możesz teraz opróżnić koszyk lub zapisać zamówienie w bazie danych
        request.session['cart'] = []  # Opróżniamy koszyk po zatwierdzeniu

    return render(request, 'orders/checkout.html.jinja', {
        'cart_items': cleaned_cart,
        'total_price': total_price,
        'order_success': order_success,  # Przekazujemy zmienną do szablonu
    })
@login_required
def checkout_view(request):
    cart = request.session.get('cart', [])
    
    # Debugowanie: sprawdzamy, co jest w koszyku
    print("Cart at checkout:", cart)

    # Jeśli koszyk jest pusty, przekieruj na stronę główną
    if not cart:
        return redirect('index')

    # Pobieramy szczegóły koszyka
    cart_items = []
    total_price = 0

    for item in cart:
        try:
            car = Car.objects.get(id=item['car_id'])
            rental_days = item.get('rental_days', 1)
            total_price += car.rent * rental_days

            cart_items.append({
                'car_id': car.id,
                'car_brand': car.brand,
                'car_model': car.model,
                'car_image': car.image.url if car.image else None,  # Sprawdzamy, czy jest obrazek
                'rental_days': rental_days,
                'total_price': car.rent * rental_days,
            })
        except Car.DoesNotExist:
            continue

    # Obsługa formularza
    if request.method == 'POST':
        # Tutaj możesz zrealizować zamówienie i zapisać je w bazie danych
        # Na przykład:
        # Order.objects.create(user=request.user, total_price=total_price, items=cart_items)

        # Wyczyść koszyk po złożeniu zamówienia
        request.session['cart'] = []

        # Przekierowanie po zakończeniu zamówienia
        return redirect('order_confirmation')  # Przekierowanie na stronę z potwierdzeniem zamówienia

    return render(request, 'orders/checkout.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
@login_required
def cart_view(request):
    cart = request.session.get('cart', [])
    
    # Debugowanie: sprawdzamy, co znajduje się w koszyku
    print("Cart:", cart)
    
    if not cart:
        return render(request, 'orders/cart.html.jinja', {
            'message': 'Twój koszyk jest pusty.'
        })

    cart_items = []
    total_price = 0

    for item in cart:
        # Sprawdzamy, czy `item` jest słownikiem
        if isinstance(item, dict):
            try:
                car = Car.objects.get(id=item['car_id'])
                rental_days = item.get('rental_days', 1)
                total_price += car.rent * rental_days

                cart_items.append({
                    'car_id': car.id,
                    'car_brand': car.brand,
                    'car_model': car.model,
                    'rental_days': rental_days,
                    'total_price': car.rent * rental_days,
                    'car_image': car.image.url if car.image else None  # Dodajemy zdjęcie
                })
            except Car.DoesNotExist:
                continue
        else:
            # Jeśli `item` nie jest słownikiem, to printujemy informację
            print(f"Item is not a dictionary: {item}")
    
    return render(request, 'orders/cart.html.jinja', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
# Zaktualizowanie dni wynajmu
@login_required

@login_required
def update_rental_days(request, car_id):
    # Pobranie koszyka z sesji
    cart = request.session.get('cart', [])
    
    # Przejdź przez koszyk, aby znaleźć samochód do aktualizacji
    for item in cart:
        if item['car_id'] == car_id:
            # Zaktualizowanie dni wynajmu
            rental_days = int(request.POST.get('rental_days', 1))
            item['rental_days'] = rental_days
            # Ponownie oblicz cenę, zakładając, że `item` ma dostęp do ceny samochodu
            try:
                car = Car.objects.get(id=car_id)
                # Konwertujemy cenę na float, aby uniknąć problemu z JSON serializowaniem Decimal
                item['total_price'] = float(car.rent * rental_days)
            except Car.DoesNotExist:
                continue
            break
    
    # Zaktualizowanie koszyka w sesji
    request.session['cart'] = cart
    
    return redirect('orders:cart')  # Przekierowanie do strony koszyka

# Potwierdzenie zamówienia
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Zbieramy informacje o zamówionych samochodach
    order_items = []
    total_price = 0
    for item in order.items.all():  # Zakładając, że Order ma powiązane OrderItem
        total_price += item.total_price  # Suma wszystkich cen

        order_items.append({
            'car_id': item.car.id,
            'car_brand': item.car.brand,
            'car_model': item.car.model,
            'rental_days': item.rental_days,
            'total_price': item.total_price,
            'car_image': item.car.image.url if item.car.image else None  # Dodajemy zdjęcie samochodu
        })

    return render(request, 'orders/order_confirmation.html.jinja', {
        'order': order,
        'order_items': order_items,  # Przekazujemy samochody w zamówieniu
        'total_price': total_price,
    })

# Usuwanie z koszyka
@login_required
def remove_from_cart(request, car_id):
    # Pobranie koszyka z sesji
    cart = request.session.get('cart', [])
    
    # Usuwanie przedmiotu z koszyka na podstawie car_id
    cart = [item for item in cart if item['car_id'] != car_id]
    
    # Zaktualizowanie koszyka w sesji
    request.session['cart'] = cart
    
    # Przekierowanie z powrotem do strony koszyka
    return redirect('orders:cart')

# Potwierdzenie
def confirmation(request):
    return render(request, 'orders/confirmation.html.jinja')
