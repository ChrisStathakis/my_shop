from django.core.cache import cache
from django.conf import settings
from .models import Product

USE_CACHE = settings.USE_CACHE


def no_cache_new_products_page():
    new_products = Product.my_query.new_products()
    return new_products


def cache_new_products_page():
    new_products = cache.get('new_products', 'has_expired')
    if new_products == "has_expired":
        new_products = no_cache_new_products_page()
        cache.add('new_products', new_products)
    return new_products


def new_products_queryset_view():
    if USE_CACHE:
        return cache_new_products_page()
    return no_cache_new_products_page()