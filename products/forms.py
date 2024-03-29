from django import forms
from django.forms import modelformset_factory
from django.forms import BaseModelFormSet
from .models import *


class CreateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['active', 'size', 'title', 'order_code']

    def __init__(self, *args, **kwargs):
        super(CreateProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'is_featured',
                  'site_active', 'active',
                  'size', 'is_service',
                  'color', 'brand',
                  'price', 'price_discount',
                  'category', 'vendor',
                  'price_buy', 'measure_unit',
                  'order_code', 'sku',
                  'qty', 'safe_stock',
                  'barcode', 'category_site',
                  'site_text', 'notes',
                  'slug'
                  ]

    def __init__(self, *args, **kwargs):
        super(UpdateProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProductAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['related_products'].queryset = Product.objects.filter(category=self.instance.category)
        self.fields['different_color'].queryset = Product.objects.filter(category=self.instance.category, 
                                                                         brand=self.instance.brand
                                                                         )


class ProductPhotoForm(forms.ModelForm):

    class Meta:
        model = ProductPhotos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductPhotoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BaseProductPhotoFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = ProductPhotos.objects.filter(product=self.model.product)


ProductPhotoFormSet = modelformset_factory(ProductPhotos,
                                           extra=4,
                                           form=ProductPhotoForm,

                                           )


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brands
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BrandForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CategorySiteForm(forms.ModelForm):

    class Meta:
        model = CategorySite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategorySiteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ColorForm(forms.ModelForm):

    class Meta:
        model = Color
        fields = ['title', 'costum_ordering', 'code_id']

    def __init__(self, *args, **kwargs):
        super(ColorForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SizeForm(forms.ModelForm):

    class Meta:
        model = Size
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SizeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VendorForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = "__all__"
        exclude = ["date_added",]

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SizeAttributeForm(forms.ModelForm):
    # product_related = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput(), required=True)
    # price_buy = forms.DecimalField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = SizeAttribute
        fields = ['title', 'product_related', 'qty', 'price_buy']

    def __init__(self, *args, **kwargs):
        super(SizeAttributeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GiftCreateForm(forms.ModelForm):

    class Meta:
        model = Gifts
        fields = ['title', 'status', 'gift_message']

    def __init__(self, *args, **kwargs):
        super(GiftCreateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GiftEditForm(forms.ModelForm):

    class Meta:
        model = Gifts
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GiftEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control col-md-6'