from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import (
    Product, CategorySite, SizeAttribute,
    Size, Characteristics, CharacteristicsValue,
    Color, ProductCharacteristics, ProductPhotos
)
from site_settings.admin_tools import admin_link
from site_settings.admin_mixins import DefaultFilterMixin
from .inlines import PhotoInline


@admin.register(Characteristics)
class CharacteristicsAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title']


@admin.register(CharacteristicsValue)
class CharacteristicsValueAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title']


@admin.register(ProductCharacteristics)
class ProductCharacteristicsAdmin(admin.ModelAdmin):
    list_display = ['title', 'value']
    autocomplete_fields = ['title', 'value']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    search_fields = ['title']
    list_filter = ['title']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    search_fields = ['title']
    list_filter = ['title']


@admin.register(Product)
class ProductAdmin(DefaultFilterMixin, ImportExportModelAdmin):
    list_display = ['title', 'category_link', 'vendor_link', 'tag_final_price', 'qty', 'active']
    list_filter = ['active', 'site_active', 'is_offer', 'category', 'vendor']
    list_select_related = ['category', 'vendor']
    readonly_fields = ['tag_final_price', ]
    autocomplete_fields = ['vendor', 'category']
    save_as = True
    list_per_page = 50
    search_fields = ['title']
    inlines = [PhotoInline, ]
    fieldsets = (
        ('Αποθήκη', {
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
            # 'active': True,
            'site_active': True
        }


@admin.register(SizeAttribute)
class SizeAttributeAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_related', 'qty']
    search_fields = ['title', 'product_related__title']
    list_per_page = 50
    list_select_related = ['product_related']


@admin.register(ProductPhotos)
class ProductPhotosAdmin(admin.ModelAdmin):
    list_display = ['tag_image_tiny', '__str__', 'is_primary', 'active']
    readonly_fields = ['tag_image_tiny']
    list_display_links = ['tag_image_tiny', '__str__']
    search_fields = ['product__title']
