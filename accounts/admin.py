from django.contrib import admin
from .models import CostumerAccount, BillingProfile

admin.site.register(CostumerAccount)
admin.site.register(BillingProfile)