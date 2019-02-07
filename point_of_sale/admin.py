from django.contrib import admin
from django.db.models import Count, Sum, Min, Max
from django.db.models import DateField
from django.db.models.functions import Trunc
from .models import RetailOrderItem, RetailOrder, GiftRetailItem
from import_export.admin import ImportExportModelAdmin

from products.models import Product
# Register your models here.


class RetailOrderInline(admin.TabularInline):
    model = RetailOrderItem
    fields = ['title', 'order', 'qty', 'is_find', 'tag_final_value']
    autocomplete_fields = ['title']
    readonly_fields = ['tag_final_value', ]
    extra = 3

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object = obj
        return super(RetailOrderInline, self).get_formset(request, obj, **kwargs)

    '''
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(RetailOrderInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'title':
            field.queryset = Product.my_query.active_for_site()
        return field
    '''

    def get_readonly_fields(self, request, obj):
        print('read only!', self.readonly_fields, obj)
        return self.readonly_fields


@admin.register(RetailOrder)
class RetailOrderAdmin(admin.ModelAdmin):
    save_as = True
    list_per_page = 50
    list_display = ['date_expired', 'title', 'order_type','costumer_account',  'tag_final_value', 'is_paid', ]
    list_filter = ['is_paid', 'date_expired', 'order_type']
    list_select_related = ['costumer_account', ]
    inlines = [RetailOrderInline]
    fieldsets = (
        ('General', {
            'fields': (
                ('is_paid', 'order_type', 'payment_method'),
                ('title', 'seller_account'),
                ('tag_final_value', 'date_expired')

                )
        }),
        ('Eshop', {
            'fields': (
                ('status', 'costumer_account', ),
                ('shipping', 'shipping_cost', 'payment_cost'),
                ('day_sent', 'eshop_order_id', 'eshop_session_id'),
                ('cart_related', 'coupons')
            )
        }),
    )

    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['seller_account'].initial = request.user
        form.base_fields['payment_method'].initial = 1
        id = RetailOrder.objects.last().id if RetailOrder.objects.exists() else 0
        form.base_fields['title'].initial = f'Λιανική Πώληση {id+1}'
        return form

    def get_readonly_fields(self, request, obj=None):
        my_list = ['tag_final_value', 'is_paid']
        return my_list





admin.site.register(RetailOrderItem)
admin.site.register(GiftRetailItem)