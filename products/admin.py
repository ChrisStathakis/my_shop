from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import Product, CategorySite, SizeAttribute, Characteristics, CharacteristicsValue, Color
from site_settings.admin_tools import admin_link
from site_settings.admin_mixins import DefaultFilterMixin

@admin.register(Product)
class ProductAdmin(DefaultFilterMixin, ImportExportModelAdmin):
    list_display = ['title', 'category', 'vendor', 'category_link']
    list_filter = ['site_active']
    list_select_related = ['category', 'vendor']
    readonly_fields = ['tag_final_price',]
    fieldsets = (
        ('General', {
            'fields': (('site_active', 'title', 'size'),
                       ('is_featured', 'brand', 'category_site'),
                       ('qty', 'sku', 'color',),
                       ('price', 'price_discount', 'tag_final_price'),
                       ('site_text', 'slug')
                       )
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (),
        }),
    )

    @admin_link('category', _('Category'))
    def category_link(self, category):
        return category

    def get_default_filters(self, request):
        return {
            'active': True,
            'site_active': True
        }

    
