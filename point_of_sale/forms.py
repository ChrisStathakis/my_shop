from django import forms
from .models import *



#  --------------------------------------Retail Order----------------------------------------------


class RetailOrderItemAdminForm(forms.ModelForm):
    old_product = None
    new_product = None
    title = forms.ModelChoiceField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = RetailOrderItem
        fields = '__all__'

    def clean_title(self):
        try:
            old_title = self.instance.title
        except:
            old_title = self.cleaned_data.get('title')
        new_title = self.cleaned_data.get('title')
        self.new_product, self.old_product = new_title, old_title
        return new_title

    def save(self, commit=False):
        data = super(RetailOrderItemAdminForm, self).save(commit=True)
        data.save()
        new_product, old_product = self.new_product, self.old_product
        if new_product != old_product:
            old_product.qty += self.cleaned_data.get('qty')
            old_product.save()
            new_product.qty -= self.cleaned_data.get('qty')
            new_product.save()
        return data


class RetailOrderAdminForm(forms.ModelForm):
    old_costumer = None
    new_costumer = None
    costumer_account = forms.ModelChoiceField(queryset=CostumerAccount.objects.all(),
                                              required=True,
                                              #initial=CostumerAccount.objects.first()
                                            )

    class Meta:
        model = RetailOrder
        fields = "__all__"

    def clean_costumer_account(self):
        new_costumer = self.cleaned_data.get('costumer_account')
        if not new_costumer:
            new_costumer = CostumerAccount.objects.get(id=1)
        try:
            old_costumer = self.instance.costumer_account
            if not old_costumer:
                old_costumer = new_costumer
        except:
            old_costumer = new_costumer
        self.old_costumer, self.new_costumer = old_costumer, new_costumer
        return new_costumer

    def save(self, commit=True):
        data = super(RetailOrderAdminForm, self).save(commit=False)
        data.save()
        old_costumer, new_costumer = self.old_costumer, self.new_costumer
        if old_costumer != new_costumer:
            value = self.cleaned_data.get('final_price')
            paid = self.cleaned_data.get('paid_value')
            #old_costumer.balance -= value-paid
            old_costumer.save()
        return data


class SalesForm(forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = RetailOrder
        fields = ['title',
                  'costumer_account',
                  'date_expired',
                  'status',
                  'payment_method',
                  'discount',
                  'user_account'
                  ]
    def __init__(self, *args, **kwargs):
        super(SalesForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class RetailOrderItemForm(forms.ModelForm):

    class Meta:
        model = RetailOrderItem
        fields = '__all__'


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = RetailOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class EshopRetailForm(forms.ModelForm):

    class Meta:
        model = RetailOrder
        fields = ['date_expired', 'title', 
                  'payment_method', 'shipping',
                  'status', 'notes',
                  'shipping_cost', 'payment_cost'
                ]

    def __init__(self, *args, **kwargs):
        super(EshopRetailForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class EshopOrderItemForm(forms.ModelForm):

    class Meta:
        model = RetailOrderItem
        fields = ['qty',
                  'value',
                  'discount_value'
                  ]

    def __init__(self, *args, **kwargs):
        super(EshopOrderItemForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class EshopOrderItemWithSizeForm(forms.ModelForm):

    class Meta:
        model = RetailOrderItem
        fields = ['qty',
                  'value',
                  'discount_value',
                  'size',  
                  ]

    def __init__(self, *args, **kwargs):
        super(EshopOrderItemWithSizeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreateOrderItemWithSizeForm(forms.ModelForm):

    class Meta:
        model = RetailOrderItem
        fields = ['order', 'title', 'value', 'discount_value', 'qty', 'size']

    def __init__(self, *args, **kwargs):
        super(CreateOrderItemWithSizeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class RetailOrderWarehouseIncomeForm(forms.ModelForm):

    class Meta:
        model = RetailOrder
        fields = ['title', 'user_account', 'notes']

    def __init__(self, *args, **kwargs):
        super(RetailOrderWarehouseIncomeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ShippingForm(forms.ModelForm):

    class Meta:
        model = Shipping
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CouponForm(forms.ModelForm):
     
    class Meta:
        model = Coupons
        fields = "__all__"
        

