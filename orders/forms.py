from django.db import models
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    apartment_number = forms.CharField(required=False, max_length=20)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'birth_date', 'email', 'phone_number',
            'street', 'city', 'postal_code', 'house_number', 'apartment_number', 'payment_method'
        ]

from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Napisz swoją opinię...',
                'class': 'form-control'
            })
        }
        labels = {
            'content': 'Treść opinii',
        }