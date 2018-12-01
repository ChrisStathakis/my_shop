from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


@admin.register(Brands)
class BrandsAdmin(ImportExportModelAdmin):
    pass


@admin.register(CategorySite)
class CategorySiteAdmin(ImportExportModelAdmin):
    pass

