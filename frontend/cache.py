from django.core.cache import cache
from .models import FirstPage, Banner
from .models import CategorySite
from products.models import Product

USE_CACHE = True


def no_cache_homepage():
    first_page = FirstPage.active_first_page()
    featured_products = Product.my_query.get_site_queryset().featured()
    banners = Banner.objects.filter(active=True)
    return [first_page, featured_products, banners]


def cache_homepage():
    first_page = cache.get('first_page', 'has_expires')
    if first_page == 'has_expired':
        first_page = FirstPage.active_first_page()
        cache.add('first_page', first_page)

    featured_products = cache.get('featured_products', 'has_expired')
    if featured_products == 'has_expired':
        featured_products = Product.my_query.get_site_queryset().featured()
        cache.add('featured_products', featured_products)

    banners = cache.get('banners', 'has_expired')
    if banners == 'has_expired':
        banners = Banner.objects.filter(active=True)
        cache.add('banners', banners)
    return [first_page, featured_products, banners]


def homepage_view_data():
    if USE_CACHE:
        return cache_homepage()
    return no_cache_homepage()


def no_cache_navbar_categories():
    menu_categories = CategorySite.my_query.navbar()
    return menu_categories


def cache_navbar_categories():
    menu_categories = cache.get('navbar_categories', 'has_expired')
    if menu_categories == 'has_expired':
        menu_categories = no_cache_navbar_categories()
        cache.add('navbar_categories', menu_categories)
    return menu_categories


def navbar_categgories_view_data():
    if USE_CACHE:
        return cache_navbar_categories()
    return no_cache_navbar_categories()