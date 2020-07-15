from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import UserProfile
from django.contrib.auth.models import User


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayTm')
)

class CheckoutForm(forms.Form):
    street_address=forms.CharField(widget=forms.TextInput(attrs={
             'placeholder':'Vadodara'
    }))
    apartment_address=forms.CharField(required=False,widget=forms.TextInput(attrs={
             'placeholder':'Ankleshwar'
    }))
    billing_country=CountryField(blank_label='(select country)').formfield(required=False,widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    zip=forms.CharField()
    same_billing_address=forms.BooleanField(widget=forms.CheckboxInput())
    save_info=forms.BooleanField(widget=forms.CheckboxInput())
    #payment_option=forms.BooleanField(widget=forms.RadioSelect,choices=PAYMENT_CHOICES)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class UserProfileForm(forms.ModelForm):
    class Meta():
        model=User
        fields=('username','email')

class OtherUpdateForm(forms.ModelForm):
    class Meta():
        model=UserProfile
        fields=('photo','phone_number','state','city')
