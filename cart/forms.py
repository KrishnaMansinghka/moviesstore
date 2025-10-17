from django import forms
from .models import Order

class StateSelectionForm(forms.Form):
    state = forms.ChoiceField(
        choices=Order.STATE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select your state'
    )
