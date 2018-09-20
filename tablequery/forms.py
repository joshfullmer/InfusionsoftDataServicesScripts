from django import forms
from django.forms.widgets import TextInput

from services.constants import FIELDS


class QueryForm(forms.Form):
    app_name = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'Infusionsoft App Name'}))
    api_key = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'API Key'}))
    TABLE_CHOICES = [(tablename, tablename) for tablename in FIELDS.keys()]
    tablename = forms.CharField(
        label='',
        widget=forms.Select(choices=TABLE_CHOICES))
