from django.contrib import admin
from .models import Payroll


class PayrollInline(admin.TabularInline):
    model = Payroll
    extra = 1
    fields = ['title', 'date_expired', 'person', 'value', 'category']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


