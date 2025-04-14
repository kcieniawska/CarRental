from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm  # Zaimportuj formularze
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import Order

# Widok rejestracji
@never_cache
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Zalogowanie użytkownika po rejestracji
            return redirect('/')  # Możesz przekierować na stronę główną lub inną
    else:
        form = CustomUserCreationForm()

    # Renderowanie formularza rejestracji
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
                return redirect('/')  # Po zalogowaniu, przekieruj na stronę główną
            else:
                form.add_error(None, "Nieprawidłowy login lub hasło")
    else:
        form = AuthenticationForm()
    
    # Renderowanie formularza logowania
    return render(request, 'users/login.html.jinja', {'form': form})

# Widok edycji profilu
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Po zapisaniu, przekieruj na stronę profilu
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    # Renderowanie formularza edycji profilu
    return render(request, 'users/edit_profile.html.jinja', {'form': form})

# Widok wylogowania
def logout_view(request):
    logout(request)  # Wylogowanie użytkownika
    return redirect('index')  # Przekierowanie na stronę główną

# Widok koszyka
def cart(request):
    # Na razie pokazujemy tylko prostą stronę koszyka.
    # Tutaj możesz pobierać przedmioty z sesji, bazy danych itd.
    return render(request, 'cars/cart.html.jinja')

# Widok profilu
def profile(request):
    return render(request, 'users/profile.html.jinja')  # Lub inny szablon, który wyświetla profil

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'my_orders.html.jinja', {'orders': orders})