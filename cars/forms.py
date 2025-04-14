from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'bio', 'profile_picture')
        widgets = {
            'birth_date': forms.SelectDateWidget(years=range(1900, 2025)),
        }