from django import forms

from django.contrib.contenttypes.models import ContentType
from .models import PaymentOrders, PaymentMethod


class PaymentForm(forms.ModelForm):
    object_id = forms.IntegerField(widget=forms.HiddenInput())
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all(), widget=forms.HiddenInput())
    is_expense = forms.BooleanField(widget=forms.HiddenInput())
    date_expired = forms.DateField(widget=forms.DateInput(attrs={'type': 'date',}))

    class Meta:
        model = PaymentOrders
        fields = ['date_expired', 'value', 'title', 'payment_method', 'is_check', 'is_paid', 'content_type', 'object_id']
        exclude = ['date_created', ]

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PaymentMethodForm(forms.ModelForm):

    class Meta:
        model = PaymentMethod
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


