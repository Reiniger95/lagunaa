from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Reservation
from datetime import date, timedelta, time
class RegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, label="Telefone")

    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=None,  # Remove o help text padrão
    )
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=None,  # Remove o help text padrão
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password1', 'password2']
        labels = {
            'email': 'Email',
            'phone': 'Telefone',
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")

class DateForm(forms.Form):
    date = forms.DateField(
        label='',  # Define uma label vazia para remover a string "Date"
        widget=forms.TextInput(attrs={
            'id': 'id_date',
            'class': 'flatpickr',
            'data-date-format': 'Y-m-d',
            'data-min-date': date.today().strftime('%Y-%m-%d'),
            'data-max-date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
        }),
        initial=date.today,
    )
class TimeSlotForm(forms.Form):
    time_slot = forms.ChoiceField(
        choices=[(time(hour, 0).strftime('%H:%M'), f"{hour}:00") for hour in range(8, 23)],
        widget=forms.RadioSelect
    )
class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'flatpickr',
            'data-date-format': 'Y-m-d',
            'data-min-date': date.today().strftime('%Y-%m-%d'),
            'data-max-date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
        }),
        initial=date.today,
    )

    class Meta:
        model = Reservation
        fields = ['court', 'date', 'time_slot']