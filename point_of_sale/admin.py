from django.contrib import admin
from .models import RetailOrderItem, RetailOrder
# Register your models here.


admin.site.register(RetailOrderItem)
admin.site.register(RetailOrder)