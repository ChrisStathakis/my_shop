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
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

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


class PayrollActionForm(forms.Form):
    comment = forms.CharField(required=False, widget=forms.Textarea, )
    send_email = forms.BooleanField(required=False, )

    @property
    def email_subject_template(self):
        return 'email/account/notification_subject.txt'

    @property
    def email_body_template(self):
        raise NotImplementedError()

    def form_action(self, account, user):
        raise NotImplementedError()

    def save(self, account, user):
        try:
            account, action = self.form_action(account, user)
        except:
            pass
        if self.cleaned_data.get('send_email', False):
            print('send_email')

        return account, action


class PayForm(PayrollActionForm):
    value = forms.DecimalField(required=True, help_text='How much?')

    field_order = (
        'value',
        'send_email'
    )

    def form_action(self, account, user):
        return Payroll.objects.create(

        )