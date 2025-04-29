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
from django.db.models import Count, Q, Avg
from orders.models import Order, Review
from datetime import date
# Ustawienie loggera
logger = logging.getLogger(__name__)

from django.db.models import Count, Q, Avg



def index(request):
    # Samochody polecane
    recommended_cars = Car.objects.filter(is_recommended=True)[:3]

    # Najczęściej wynajmowane samochody
    most_rented = Car.objects.annotate(
        order_count=Count('orders')  # Liczymy zamówienia powiązane z samochodami
    ).order_by('-order_count')[:3]

    # Dostępne samochody
    available_cars = Car.objects.filter(is_available=True)

    # Zaktualizuj dostępność dla każdego samochodu
    available_cars = [car for car in available_cars if car.is_currently_available()]

    context = {
        'available_cars': available_cars,
    }

    # Najczęściej oceniane
    most_reviewed = Car.objects.annotate(
        reviews_count=Count('car_reviews')  # Liczymy recenzje powiązane z samochodami
    ).filter(reviews_count__gt=0)  # Tylko samochody z recenzjami

    # Dodanie średniej oceny dla samochodów na podstawie recenzji
    most_reviewed = most_reviewed.annotate(
        avg_rating=Avg('car_reviews__rating')  # Liczymy średnią ocenę z recenzji
    )

    # Sortowanie według liczby recenzji i średniej oceny
    most_reviewed = most_reviewed.order_by('-reviews_count', '-avg_rating')[:3]

    return render(request, 'cars/index.html.jinja', {
        'available_cars': available_cars,
        'recommended_cars': recommended_cars,
        'most_rented_cars': most_rented,
        'most_reviewed_cars': most_reviewed,
    })
# Strona szczegółów samochodu

def car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    # Ustawienie dostępności i dat
    car.set_availability()

    # Pobranie zatwierdzonych opinii
    reviews = Review.objects.filter(car=car, is_approved=True)

    # Pobranie oczekujących opinii (niezatwierdzonych)
    pending_reviews = Review.objects.filter(car=car, is_approved=False)

    # Sprawdzamy, czy użytkownik jest moderatorem
    is_moderator = request.user.is_staff

    # Jeśli użytkownik jest zalogowany, pobieramy jego opinie
    if request.user.is_authenticated:
        user_reviews = Review.objects.filter(user=request.user, car=car)
    else:
        user_reviews = None

    average_rating = car.car_reviews.aggregate(Avg('rating'))['rating__avg']
    if not average_rating:
        average_rating = 0.0

    context = {
        'car': car,
        'reviews': reviews,
        'pending_reviews': pending_reviews,
        'is_moderator': is_moderator,
        'user_reviews': user_reviews,
        'is_available': car.is_available,
        'rental_start_date': car.rental_start_date,
        'rental_end_date': car.rental_end_date,
        'average_rating': average_rating,
    }

    return render(request, 'cars/car.html.jinja', context)
    
def all_cars_view(request):
    cars = Car.objects.all()  # lub filtrujesz, jak chcesz
    return render(request, 'cars/cars.html.jinja', {'cars': cars})

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
