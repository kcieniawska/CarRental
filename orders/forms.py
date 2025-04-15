from django import forms
from .models import Order
from .models import Car

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'street', 'city', 'postal_code', 'house_number', 'payment_method', 'car', 'start_date', 'end_date']

    # Możesz ustawić pola jako wymagane w formularzu
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    street = forms.CharField(max_length=200, required=False)  # Możesz ustawić na `required=True`, jeśli jest wymagane
    city = forms.CharField(max_length=100, required=True)  # Wymagane
    postal_code = forms.CharField(max_length=20, required=True)  # Wymagane
    house_number = forms.CharField(max_length=20, required=True)  # Wymagane
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHODS, required=True)  # Wymagane
    
    # Dodajemy pole na samochód (wybór samochodu do wynajmu)
    car = forms.ModelChoiceField(queryset=Car.objects.all(), required=True)

    # Dodajemy pola na daty wynajmu (rozpoczęcia i zakończenia)
    start_date = forms.DateField(required=True, widget=forms.SelectDateWidget)
    end_date = forms.DateField(required=True, widget=forms.SelectDateWidget)
