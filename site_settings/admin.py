from django.contrib import admin
from .models import PaymentOrders, PaymentMethod

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentOrders)
class PaymentOrders(admin.ModelAdmin):
    pass
