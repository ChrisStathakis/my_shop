from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Product, CategorySite, SizeAttribute, Characteristics, CharacteristicsValue, Color
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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

