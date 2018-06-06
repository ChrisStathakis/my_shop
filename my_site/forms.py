from django import forms
from .models import *

from site_settings.models import PaymentMethod
from .models import Shipping
from .validators import validate_cellphone, validate_number


class ShippingForm(forms.ModelForm):
    
    class Meta:
        model = Shipping
        fields = '__all__'
        exclude = ['country',]

    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BannerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class FirstPageForm(forms.ModelForm):

    class Meta:
        model = FirstPage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    

class CheckoutForm(forms.Form):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    zip_code = forms.CharField(required=True, 
                               widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}),
                               validators=[validate_number]
                               )
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    cellphone = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'CellPhone'}),
                                validators=[validate_cellphone]
                                )

    notes = forms.Textarea()
    payment_method = forms.ModelChoiceField(required=True, queryset=PaymentMethod.objects.all())
    shipping_method = forms.ModelChoiceField(required=True, queryset=Shipping.objects.all())
    agreed = forms.BooleanField(required=True)

    
    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
