from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from mptt.admin import DraggableMPTTAdmin


@admin.register(Brands)
class BrandsAdmin(ImportExportModelAdmin):
    list_display = ['title', 'active']
    readonly_fields = ['tag_image']
    fields = ['active', 'title', 'tag_image', 'image', 'slug', 'meta_description']
    list_filter = ['active']
    search_fields = ['title']
    list_per_page = 30


@admin.register(CategorySite)
class CategorySiteAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'active', ]
    search_fields = ['name', ]
    list_filter = ['active']
    list_display_links = ['indented_title', ]
    list_per_page = 30




