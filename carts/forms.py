from django import forms
from .models import CartItem, Cart, PaymentMethod, Shipping
from products.models import Product, SizeAttribute
from .models import Coupons


class CartItemForm(forms.Form):
    qty = forms.IntegerField(required=True,
                             min_value=1,
                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                             'placeholder': 1,
                                                             'value': 1,
                                                             }),
                             )


class CartItemNoAttrForm(forms.ModelForm):
    order_related = forms.ModelChoiceField(queryset=Cart.objects.all(),
                                   widget=forms.HiddenInput(),
                                   )
    product_related = forms.ModelChoiceField(queryset=Product.my_query.active_for_site(),
                                             widget=forms.HiddenInput(),
                                             )
    id_session = forms.CharField(widget=forms.HiddenInput())
    price = forms.DecimalField(widget=forms.HiddenInput())
    # price_discount

    class Meta:
        model = CartItem
        fields = ['order_related',
                  'product_related',
                  'id_session',
                  'qty',
                  'price',
                  'price_discount',
                   ]

    def __init__(self, *args, **kwargs):
        super(CartItemNoAttrForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CouponQuickForm(forms.ModelForm):
    date_created = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Coupons
        fields = ['active', 'title', 'code', 'date_created', 'date_end']

    def __init__(self, *args, **kwargs):
        super(CouponQuickForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CouponForm(forms.ModelForm):
    date_created = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Coupons
        fields = '__all__'
        exclude = ['products', 'categories']

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CartItemCreate(forms.Form):
    qty = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                            'placeholder': '1',
                                                                            'value': '1',
                                                                            'min': 1,
                                                                            })
                                                                            )
    # size = forms.ModelChoiceField(re)


class CartItemCreateWithAttrForm(forms.Form):
    qty = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                            'placeholder': "1",
                                                                            'value': '1',
                                                                            'min': 1,
                                                                            })
                                                                    )
    attribute = forms.ModelChoiceField(required=True,
                                       queryset=SizeAttribute.objects.all(),
                                       widget=forms.Select(attrs={'class': 'form-control',
                                                           })
                                       )

    def __init__(self, instance_related=None, *args, **kwargs):
        super(CartItemCreateWithAttrForm, self).__init__(*args, **kwargs)
        print(instance_related)
        if instance_related:
            self.fields['attribute'].queryset = SizeAttribute.objects.filter(product_related=instance_related)


class CartCostumerForm(forms.Form):
    add_coupon = forms.CharField(required=False)
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.all(), required=False)
    shipping_method = forms.ModelChoiceField(queryset = Shipping.objects.all(), required=False)

    class Meta:
        fields = ['payment_method', 'shipping_method', 'add_coupon']

    def __init__(self, instance_related=None, *args, **kwargs):
        super(CartCostumerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['payment_method'].queryset = PaymentMethod.my_query.active_for_site()
        self.fields['shipping_method'].queryset = Shipping.objects.filter(active=True)
