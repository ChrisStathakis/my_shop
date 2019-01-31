from django.contrib import admin
from .models import PaymentMethod, Shipping, Store


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_additional_cost', 'tag_limit_value', 'active']
    list_filter = ['active']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_additional_cost', 'tag_limit_value', 'site_active', 'active']
    list_filter = ['active', 'site_active']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']