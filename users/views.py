from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Order
from django.conf import settings

# Widok rejestracji
@never_cache
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Zalogowanie użytkownika po rejestracji
            return redirect('/')  # Przekierowanie na stronę główną po udanej rejestracji
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

# Widok edycji profilu
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'users/edit_profile.html.jinja', {'form': form})
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
    # Pobieramy zamówienia użytkownika
    orders = Order.objects.filter(user=request.user)
    print(f"User: {request.user.username}")  # Sprawdź, kto jest zalogowany
    print(f"Orders: {orders}")  # Sprawdź, jakie zamówienia są zwracane
    return render(request, 'users/profile.html.jinja', {'orders': orders})

# Widok zamówień użytkownika
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    print(f"Orders for {request.user.username}: {orders}")  # Zobaczmy, jakie zamówienia są zwracane
    return render(request, 'users/my_orders.html.jinja', {'orders': orders})
