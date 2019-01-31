from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Order, OrderItem, Category, Vendor, OrderItemSize, WarehouseOrderImage




class OrderPhotoInline(admin.TabularInline):
    model = WarehouseOrderImage
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 3
    fields = ['product', 'value', 'qty', 'discount_value', 'unit', 'tag_final_value', 'total_clean_value']
    autocomplete_fields = ['product']
    search_fields = ['product__title']

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
