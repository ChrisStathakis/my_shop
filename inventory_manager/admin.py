from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import *
from site_settings.admin_tools import admin_changelist_link


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