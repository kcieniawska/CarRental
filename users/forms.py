# users/forms.py
from django import forms
from .models import CustomUser

# Formularz do rejestracji użytkownika
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Potwierdź hasło", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'birth_date']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hasła muszą się zgadzać.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)  # Pobranie instancji użytkownika
        user.set_password(self.cleaned_data["password1"])  # Ustawienie hasła w postaci zahashowanej
        if commit:
            user.save()  # Zapisanie użytkownika w bazie danych
        return user


# Formularz do edycji danych użytkownika
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'bio', 'profile_picture', 'birth_date']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
