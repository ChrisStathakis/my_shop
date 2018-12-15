from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderItem, Category, Vendor, OrderItemSize, WarehouseOrderImage
from site_settings.admin_tools import admin_changelist_link
from site_settings.models import PaymentOrders


def update_vendor(modeladmin, request, queryset):
    for order in queryset:
        items = order.order_items.all()
        for item in items:
            product = item.product
            product.vendor = order.vendor
            product.save()


class PaymentOrderInline(GenericTabularInline):
    model = PaymentOrders
    extra = 1
    fields = ['title', 'date_expired', 'payment_method', 'value', 'is_paid']


class OrderPhotoInline(admin.TabularInline):
    model = WarehouseOrderImage
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'value', 'qty', 'discount_value', 'unit', 'tag_final_value', 'total_clean_value']

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object = obj
        return super(OrderItemInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(OrderItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'product':
            if self.parent_object is not None:
                field.queryset = field.queryset.filter(vendor=self.parent_object.vendor)
            else:
                field.queryset = field.queryset.none()
        return field

    def get_readonly_fields(self, request, obj=None):
        my_list = ['tag_final_value', ]
        return my_list


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ['date_expired', 'title', 'vendor', 'is_paid', 'tag_final_value']
    list_select_related = ['vendor']
    list_per_page = 50
    list_filter = ['vendor', 'is_paid']
    inlines = [OrderPhotoInline, OrderItemInline, PaymentOrderInline]
    actions = [update_vendor, ]

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

    def response_add(self, request, new_object):
        obj = self.after_saving_model_and_related_inlines(new_object)
        return super(OrderAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        obj = self.after_saving_model_and_related_inlines(obj)
        return super(OrderAdmin, self).response_change(request, obj)

    def after_saving_model_and_related_inlines(self, obj):
        obj.save()
        return obj

@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    pass


@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['title',]

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