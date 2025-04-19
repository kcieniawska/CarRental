from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomUserChangeForm
from orders.forms import OrderForm
from orders.models import Order, OrderItem  # Upewnij się, że importujesz OrderItem


# Widok rejestracji
@never_cache
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'users/register.html.jinja', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html.jinja', {'form': form})


# Widok logowania
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                form.add_error(None, "Nieprawidłowy login lub hasło")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html.jinja', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html.jinja')  # Twoja strona profilu
# Widok edycji profilu
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        user.save()
        messages.success(request, 'Profil został pomyślnie zaktualizowany!')

        return redirect('users:profile')  # Upewnij się, że używasz prefiksu 'users:'
    
    return render(request, 'users/edit_profile.html.jinja')

# Widok wylogowania
def logout_view(request):
    logout(request)
    return redirect('index')


# Widok koszyka
def cart(request):
    return render(request, 'cars/cart.html.jinja')


# Widok profilu
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)  # Pobieramy zamówienia powiązane z użytkownikiem
    return render(request, 'users/profile.html.jinja', {'orders': orders})


# Widok zamówień użytkownika
@login_required
def user_orders(request, order_id):
    # Pobieramy zamówienie na podstawie ID
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'users/orders.html.jinja', {'order': order})

# Widok tworzenia zamówienia
@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  # Przypisujemy zamówienie do aktualnie zalogowanego użytkownika
            order.save()
            return redirect('profile')  # Po zapisaniu zamówienia, przekierowanie do profilu
        else:
            print("❌ BŁĘDY FORMULARZA:", form.errors)
    else:
        form = OrderForm()
    return render(request, 'users/create_order.html.jinja', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from orders.models import Review
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def add_review(request, order_id):
    # Pobierz zamówienie na podstawie order_id
    order = get_object_or_404(Order, id=order_id)
    
    # Pobierz powiązany samochód z zamówienia
    car = order.car

    if request.method == 'POST':
        # Pobierz dane z formularza
        rating = request.POST.get('rating')
        content = request.POST.get('content')

        # Sprawdź, czy dane są poprawne
        if rating and content:
            # Utwórz nową opinię
            review = Review.objects.create(
                car=car,
                user=request.user,
                rating=rating,
                content=content,
            )
            review.save()
            
            # Wyświetl komunikat o sukcesie
            messages.success(request, "Twoja opinia została pomyślnie dodana!")

            # Przekieruj do strony szczegółów samochodu
            return redirect('cars:car_detail', car_id=car.id)
        else:
            messages.error(request, "Proszę wypełnić wszystkie pola!")

    return render(request, 'users/add_review.html.jinja', {'car': car, 'order': order})