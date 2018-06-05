from django import forms
from .models import *


class ShippingForm(forms.ModelForm):
    
    class Meta:
        model = Shipping
        fields = '__all__'
        exclude = ['country',]

    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
