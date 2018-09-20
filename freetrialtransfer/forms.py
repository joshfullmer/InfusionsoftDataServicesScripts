from django import forms
from django.forms.widgets import TextInput


class TransferForm(forms.Form):
    src_app_name = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'Source App Name'}))
    src_api_key = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'Source API Key'}))
    dest_app_name = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'Destination App Name'}))
    dest_api_key = forms.CharField(
        label='',
        widget=TextInput(attrs={'placeholder': 'Destination API Key'}))
