# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm  # Zakładając, że masz ten formularz

# Widok rejestracji
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Zalogowanie użytkownika po rejestracji
            return redirect('home')  # Możesz przekierować na stronę główną lub inną
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

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
                return redirect('home')  # Po zalogowaniu, przekieruj na stronę główną
            else:
                form.add_error(None, "Nieprawidłowy login lub hasło")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

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
    
    return render(request, 'users/edit_profile.html', {'form': form})
