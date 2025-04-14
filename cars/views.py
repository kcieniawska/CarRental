import logging
from django.shortcuts import render, get_object_or_404, redirect
from .models import Car
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

logger = logging.getLogger(__name__)

def index(request):
    cars = Car.objects.all()  # Pobieranie wszystkich samochodów
    return render(request, 'cars/index.html.jinja', {'cars': cars})

def car(request, car_id):
    car = get_object_or_404(Car, id=car_id)  # Automatycznie zwróci błąd 404, jeśli car_id nie istnieje
    return render(request, 'cars/car.html.jinja', {'car': car})


def category_list(request):
    # Pobieramy wszystkie unikalne kategorie samochodów
    categories = Car.objects.values_list('category', flat=True).distinct()
    
    # Tworzymy mapowanie z kodów kategorii na pełne nazwy
    category_dict = dict(Car.CAR_CLASSES)
    
    # Tworzymy listę z kodami i pełnymi nazwami kategorii
    category_info = [(code, category_dict.get(code)) for code in categories]
    
    return render(request, 'cars/category_list.html.jinja', {'categories': category_info})

def category_view(request, category):
    # Pobieramy pełną nazwę kategorii na podstawie kodu (np. 'a' → 'małe i mini')
    category_dict = dict(Car.CAR_CLASSES)
    full_category_name = category_dict.get(category, "Nieznana kategoria")  # Domyślnie, jeśli nie znajdzie kategorii

    # Filtrowanie samochodów według kategorii
    cars_in_category = Car.objects.filter(category=category)
    
    return render(request, 'cars/category.html.jinja', {
        'cars': cars_in_category,
        'category': full_category_name,
    })

def contact(request):
    return render(request, 'cars/contact.html.jinja')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Po udanej rejestracji przekierowanie na stronę logowania
    else:
        form = CustomUserCreationForm()
    return render(request, 'cars/register.html.jinja', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Przekierowanie po udanym logowaniu, np. na stronę główną
    else:
        form = AuthenticationForm()
    
    return render(request, 'cars/login.html.jinja', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')  # Przekierowanie po wylogowaniu
