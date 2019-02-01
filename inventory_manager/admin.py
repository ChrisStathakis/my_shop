from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from django.http import HttpResponse
from django.urls import path
from import_export.admin import ImportExportModelAdmin
import csv
from .models import Order, OrderItem, Category, Vendor, OrderItemSize, WarehouseOrderImage
from .filters import HaveDeptFilter
from .inlines import OrderItemInline, OrderPhotoInline
from .actions import update_vendor
from site_settings.admin_tools import admin_changelist_link


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ['date_expired', 'title', 'order_type', 'vendor', 'is_paid', 'tag_final_value']
    list_select_related = ['vendor']
    list_per_page = 50
    list_filter = ['vendor', 'is_paid']
    inlines = [OrderPhotoInline, OrderItemInline]
    actions = [update_vendor, ]
    autocomplete_fields = ['vendor']
    search_fields = ['vendor']

    fieldsets = (
        ('General', {
            'fields': (
                ('is_paid', 'vendor', 'tag_remaining_value'),
                ('title', 'date_expired'),
                ('timestamp', 'edited'),
                ('order_type',  'payment_method'),
                ('taxes_modifier', 'discount',),
                ('tag_value', 'tag_total_discount', 'tag_clean_value'), 
                ('tag_total_taxes', 'tag_final_value'),
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        obj_list = ['timestamp', 'edited', 'tag_final_value',
                    'tag_value', 'tag_total_discount', 'tag_clean_value', 
                    'tag_total_taxes', 'tag_final_value', 'is_paid', 'tag_remaining_value'
                    ]
        if obj:
            obj_list.append('vendor')
            if obj.is_paid:
                obj_list.extend(['taxes_modifier', 'payment_method', 'order_type', 'date_expired', 'discount'])
        return obj_list


@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    list_display = ['__str__', 'qty', 'tag_final_value']
    readonly_fields = ['tag_final_value']
    autocomplete_fields = ['product']
    search_fields = ['product']


@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    change_list_template = 'my_admin/vendor_list.html'
    list_per_page = 20
    list_display = ['title', 'tag_balance', 'order_count']
    readonly_fields = ['tag_balance']
    list_filter = [HaveDeptFilter, ]
    search_fields = ['title', ]
    actions = ['export_as_csv', ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _order_count=Count('vendor_orders', distinct=True)
        )
        return queryset

    def order_count(self, obj):
        return obj._order_count
    order_count.admin_order_field = '_order_count'
    order_count.short_description = 'Σύνολο Παραστατικών'

    def have_dept(self, obj):
        return obj.balance > 0

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        fields_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fields_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fields_names])
        return response

    export_as_csv.short_description = 'Εξαγωγή ως CSV'


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['title',]
    search_fields = ['title']

    @admin_changelist_link(
        'products',
        _('Products'), 
        query_string=lambda c: 'category_id={}'.format(c.pk)
    )
    def products_link(self, products):
        return _('Products')


@admin.register(OrderItemSize)
class OrderItemSixeAdmin(admin.ModelAdmin):
    pass