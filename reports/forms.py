from django import forms


class DateCookiesChoose(forms.Form):
    date_start = forms.DateField(required=True)
    date_end = forms.DateField(required=True)