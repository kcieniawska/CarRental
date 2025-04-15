import logging
from django.shortcuts import render, get_object_or_404, redirect
from .models import Car
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import Http404
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import ReviewForm
from django.contrib import messages
# Ustawienie loggera
logger = logging.getLogger(__name__)

# Strona główna - wyświetlanie wszystkich samochodów
def index(request):
    cars = Car.objects.all()  # Pobieranie wszystkich samochodów
    return render(request, 'cars/index.html.jinja', {'cars': cars})

# Strona szczegółów samochodu
def car(request, car_id):
    try:
        car = get_object_or_404(Car, id=car_id)  # Automatycznie zwróci błąd 404, jeśli car_id nie istnieje
    except Car.DoesNotExist:
        logger.error(f"Car with id {car_id} not found.")
        raise Http404("Car not found")
    
    return render(request, 'cars/car.html.jinja', {'car': car})

# Lista kategorii samochodów
def category_list(request):
    # Pobieramy wszystkie unikalne kategorie samochodów
    categories = Car.objects.values_list('category', flat=True).distinct()
    
    # Tworzymy mapowanie z kodów kategorii na pełne nazwy
    category_dict = dict(Car.CAR_CLASSES)
    
    # Tworzymy listę z kodami i pełnymi nazwami kategorii
    category_info = [(code, category_dict.get(code)) for code in categories]
    
    return render(request, 'cars/category_list.html.jinja', {'categories': category_info})

# Strona wyświetlająca samochody z danej kategorii
def category_view(request, category):
    # Pobieramy pełną nazwę kategorii na podstawie kodu
    category_dict = dict(Car.CAR_CLASSES)
    full_category_name = category_dict.get(category, "Nieznana kategoria")  # Domyślnie, jeśli nie znajdzie kategorii
    
    # Filtrowanie samochodów według kategorii
    cars_in_category = Car.objects.filter(category=category)
    
    if not cars_in_category:
        messages.info(request, f'Brak samochodów w kategorii "{full_category_name}".')
    
    return render(request, 'cars/category.html.jinja', {
        'cars': cars_in_category,
        'category': full_category_name,
    })

def contact(request):
    return render(request, 'cars/contact.html.jinja')

# Rejestracja użytkownika
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rejestracja zakończona sukcesem! Możesz się teraz zalogować.')
            return redirect('login')  # Po udanej rejestracji przekierowanie na stronę logowania
        else:
            messages.error(request, 'Wystąpił błąd podczas rejestracji.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'cars/register.html.jinja', {'form': form})

# Logowanie użytkownika
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User {user.username} logged in successfully.')
            return redirect('index')  # Przekierowanie po udanym logowaniu, np. na stronę główną
        else:
            logger.warning(f'Login attempt failed for user {request.POST.get("username")}')
    else:
        form = AuthenticationForm()
    
    return render(request, 'cars/login.html.jinja', {'form': form})

# Wylogowanie użytkownika
def logout_view(request):
    logout(request)
    logger.info(f'User {request.user.username} logged out.')
    return redirect('index')  # Przekierowanie po wylogowaniu

@login_required
def add_review(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Sprawdzamy, czy użytkownik już dodał opinię
    if car.reviews.filter(user=request.user).exists():
        messages.warning(request, "Już dodałeś opinię dla tego samochodu.")
        return redirect('car', car_id=car.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.car = car
            review.user = request.user
            review.save()
            messages.success(request, "Twoja opinia została dodana i czeka na zatwierdzenie przez moderatora.")
            return redirect('car', car_id=car.id)
    else:
        form = ReviewForm()

    return render(request, 'cars/car.html.jinja', {
        'car': car,
        'review_form': form,
    })