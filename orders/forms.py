from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    # Dodajemy pole dla daty urodzenia
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    # Dodajemy pole dla numeru mieszkania
    apartment_number = forms.CharField(required=False, max_length=20)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'birth_date', 'email', 'phone_number',
            'street', 'city', 'postal_code', 'house_number', 'apartment_number', 'payment_method'
        ]

    # Dodatkowa walidacja, jeśli chcesz sprawdzić np. czy email jest poprawny
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email jest wymagany.")
        return email
