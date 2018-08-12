from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Product, Category, Vendor
# Register your models here.

admin.site.register(Product, ImportExportModelAdmin)
admin.site.register(Category, ImportExportModelAdmin)
