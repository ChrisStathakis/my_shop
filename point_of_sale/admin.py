from django.contrib import admin
from django.db.models import Count, Sum, Min, Max
from django.db.models import DateField
from django.db.models.functions import Trunc
from .models import RetailOrderItem, RetailOrder, GiftRetailItem
from import_export.admin import ImportExportModelAdmin
# Register your models here.


class RetailOrderInline(admin.TabularInline):
    model = RetailOrderItem
    fields = ['title', 'order', 'qty', 'is_find', 'tag_final_value']
    readonly_fields = ['tag_final_value']
    autocomplete_fields = ['title']
    extra = 3


@admin.register(RetailOrder)
class RetailOrderAdmin(admin.ModelAdmin):
    list_display = ['date_expired', 'title', 'order_type', 'tag_final_value']
    list_filter = ['is_paid', 'date_expired', 'order_type']
    list_per_page = 50
    inlines = [RetailOrderInline]
    fieldsets = (
        ('General', {
            'fields': (
                ('is_paid', 'order_type', 'payment_method'),
                ('title', 'seller_account'),
                ('tag_final_value')

                )
        }),
        ('Eshop', {
            'fields': (
                ('status', 'costumer_account',),
                ('shipping', 'shipping_cost', 'payment_cost'),
                ('day_sent', 'eshop_order_id', 'eshop_session_id'),
                ('cart_related', 'coupons')
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        my_list = ['tag_final_value', 'is_paid']
        return my_list





admin.site.register(RetailOrderItem)
admin.site.register(GiftRetailItem)