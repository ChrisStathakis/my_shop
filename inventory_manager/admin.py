from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    pass