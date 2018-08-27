from django.contrib import admin
from .models import PaymentOrders

@admin.register(PaymentOrders)
class PaymentOrders(admin.ModelAdmin):
    pass
