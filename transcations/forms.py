from django import forms
from .models import *
from decimal import Decimal


class BillForm(forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Bill
        fields = ['date_expired', 'category', 'title', 'payment_method', 'value', 'is_paid']

    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BillCategoryForm(forms.ModelForm):
    class Meta:
        model = BillCategory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BillCategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PayrollForm(forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Payroll
        fields = ['date_expired', 'title', 'person', 'payment_method', 'category', 'value', 'is_paid']

    def __init__(self, *args, **kwargs):
        super(PayrollForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['title', 'occupation', 'phone', 'phone1', 'active']

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class OccupationForm(forms.ModelForm):
    
    class Meta:
        model = Occupation
        fields = ['title', 'notes']

    def __init__(self, *args, **kwargs):
        super(OccupationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            

class GenericExpenseForm(forms.ModelForm):

    class Meta:
        model = GenericExpense
        fields = ['date_expired', 'category', 'title', 'payment_method', 'value', 'is_paid']

    def __init__(self, *args, **kwargs):
        super(GenericExpenseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GenericExpenseCategoryForm(forms.ModelForm):

    class Meta:
        model = GenericExpenseCategory
        fields = ['title',]

    def __init__(self, *args, **kwargs):
        super(GenericExpenseCategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VacationForm(forms.ModelForm):
    date_started = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Vacation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VacationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'