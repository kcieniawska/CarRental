from django.shortcuts import render
from .models import Car

def index(request):
    cars = Car.objects.all()  # Pobieranie wszystkich samochodów, jeśli to ma sens w widoku
    return render(request, 'cars/index.html.jinja', {'cars': cars})

def car(request, car_id):
    try:
        car = Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        car = None
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
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

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
    from django.contrib.auth import logout
    logout(request)
    return redirect('index')  # Przekierowanie po wylogowaniu
def cart(request):
    # logika dla koszyka
    return render(request, 'cars/cart.html.jinja')