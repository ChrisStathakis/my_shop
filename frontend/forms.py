from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button
from .models import *

from site_settings.models import PaymentMethod
from site_settings.models import Shipping
from .validators import validate_cellphone, validate_number


class CategorySiteForm(forms.ModelForm):

    class Meta:
        model = CategorySite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategorySiteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


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
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    zip_code = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}),
                               validators=[validate_number]
                               )
    #  phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    cellphone = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'CellPhone'}),
                                validators=[validate_cellphone]
                                )
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Phone'}),

                            )
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    payment_method = forms.ModelChoiceField(required=True, queryset=PaymentMethod.objects.all())
    shipping_method = forms.ModelChoiceField(required=True, queryset=Shipping.objects.all())
    agreed = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
              Column('email', css_class='form-group col-md-12 col-lg-12 mb-3')
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 col-lg-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 col-lg-6 mb-3'),
            ),
            Row(
                Column('address', css_class='form-group col-md-4 mb-3'),
                Column('zip_code', css_class='form-group col-md-4 mb-3'),
                Column('city', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('cellphone', css_class='form-group col-md-6 mb-0'),
                Column('phone', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3')
            ),
            Row(
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
                Column('shipping_method', css_class='form-group col-md-6 mb-0'),
            ),

            Row(
                Column('agreed', css_class='form-group col-md-6 mb-3')
            ),
            Submit('submit', 'Checkout', css_class='btn btn-danger',
                   )
        )
