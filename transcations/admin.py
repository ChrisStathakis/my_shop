from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export.admin import ImportExportModelAdmin

from .models import *
from .forms import *

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    pass