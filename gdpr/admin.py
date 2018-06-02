from django.contrib import admin

from .models import CookiesModel, PolicyModel


@admin.register(CookiesModel)
class CookiesModelAdmin(admin.ModelAdmin):
    pass


@admin.register(PolicyModel)
class PolicyModelAdmin(admin.ModelAdmin):
    pass
