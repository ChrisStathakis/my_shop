from django.contrib import admin
from .models import CostumerAccount, BillingProfile, Address

admin.site.register(CostumerAccount)
admin.site.register(BillingProfile)
admin.site.register(Address)