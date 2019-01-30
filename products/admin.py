from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import Product, CategorySite, SizeAttribute, Characteristics, CharacteristicsValue, Color
from site_settings.admin_tools import admin_link
from site_settings.admin_mixins import DefaultFilterMixin


@admin.register(Product)
class ProductAdmin(DefaultFilterMixin, ImportExportModelAdmin):
    list_display = ['title', 'category_link', 'vendor_link', 'tag_final_price']
    list_filter = ['active', 'site_active', 'is_offer', 'category', 'vendor']
    list_select_related = ['category', 'vendor']
    readonly_fields = ['tag_final_price', ]
    save_as = True
    list_per_page = 50
    search_fields = ['title']
    fieldsets = (
        ('General', {
            'fields': (('active', 'size'),
                       ('is_service', 'wholesale_active',),
                       ('title', 'category', 'vendor'),
                       ('order_code', 'price_buy', 'order_discount'),
                       ('qty', 'qty_kilo', 'measure_unit', 'barcode', 'safe_stock'),
                       )
        }),
        ('Price', {
            'fields': ('is_offer',
                       ('price', 'price_discount', 'tag_final_price'))
        }),
        ('Site', {
            'fields': (
                ('site_active', 'is_featured',),
                ('brand', 'slug',),
                ('sku', 'category_site', 'site_text'),
            )
        }),

    )

    @admin_link('category', _('Category'))
    def category_link(self, category):
        return category

    @admin_link('vendor', _('Προμηθευτής'))
    def vendor_link(self, vendor):
        return vendor

    def get_default_filters(self, request):
        return {
            'active': True,
            'site_active': True
        }

    
