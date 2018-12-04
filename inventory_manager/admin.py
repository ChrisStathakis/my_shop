from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import Order, OrderItem, Category, Vendor, OrderItemSize
from site_settings.admin_tools import admin_changelist_link


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product']

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object = obj
        return super(OrderItemInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(OrderItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'product':
            print(self.parent_object)
            if self.parent_object is not None:
                field.queryset = field.queryset.filter(vendor=self.parent_object.vendor)
            else:
                field.queryset = field.queryset.none()
        return field



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['date_expired', 'title', 'vendor', 'is_paid', 'tag_final_value']
    list_select_related = ['vendor']
    list_per_page = 50
    list_filter = ['vendor', 'is_paid']
    inlines = [OrderItemInline, ]

    fieldsets = (
        ('General', {
            'fields': (
                ('is_paid', ),
                ('title', 'date_expired', 'vendor'),
                ('timestamp', 'edited'),
                ('order_type',  'payment_method'),
                ('taxes_modifier', 'discount',),
                ('tag_discount', 'tag_clean_value',  'tag_total_taxes', 'tag_final_value'),
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        obj_list = ['timestamp', 'edited', 'tag_final_value',
                    'tag_clean_value', 'tag_discount', 'tag_first_value',
                    'tag_total_taxes'
                    ]
        if obj:
            obj_list.append('vendor')
        return obj_list


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
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