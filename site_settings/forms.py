from django import forms

from django.contrib.contenttypes.models import ContentType
from .models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):

    class Meta:
        model = PaymentMethod
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'



