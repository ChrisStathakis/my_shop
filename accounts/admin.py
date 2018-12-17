from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CostumerAccount
from import_export.admin import ImportExportModelAdmin

admin.site.register(CostumerAccount)


