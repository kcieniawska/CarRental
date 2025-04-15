from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Przypisanie własnych komunikatów błędów w języku polskim
        self.fields['username'].error_messages = {
            'required': 'Nazwa użytkownika jest wymagana.',
            'max_length': 'Nazwa użytkownika może mieć maksymalnie 150 znaków.',
            'invalid': 'Nazwa użytkownika zawiera niedozwolone znaki.'
        }
        self.fields['password1'].error_messages = {
            'required': 'Hasło jest wymagane.',
            'min_length': 'Hasło musi zawierać co najmniej 8 znaków.',
            'common_password': 'Hasło jest zbyt proste i powszechnie używane.',
            'numeric_password': 'Hasło nie może składać się tylko z cyfr.',
            'password_too_similar': 'Hasło nie może być zbyt podobne do Twoich innych danych.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Potwierdź swoje hasło.',
            'password_mismatch': 'Hasła nie pasują do siebie.',
        }

from .models import Review
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Napisz swoją opinię...'})
        }
        labels = {
            'content': 'Twoja opinia',
        }