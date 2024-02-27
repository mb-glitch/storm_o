from django import forms

class PacjentForm(forms.Form):
    imie = forms.CharField(label='Imię pacjenta', max_length=100)
