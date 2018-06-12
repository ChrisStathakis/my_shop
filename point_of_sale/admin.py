from django.contrib import admin
from .models import RetailOrderItem, RetailOrder, GiftRetailItem
# Register your models here.


admin.site.register(RetailOrderItem)
admin.site.register(RetailOrder)
admin.site.register(GiftRetailItem)