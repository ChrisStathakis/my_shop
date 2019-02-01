from django.contrib import admin
from .models import ProductPhotos


class PhotoInline(admin.TabularInline):
    model = ProductPhotos
    fields = ['tag_image_tiny', 'image', 'product', 'is_primary', 'active' ]
    readonly_fields = ['tag_image_tiny']