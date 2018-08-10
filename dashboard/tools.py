from products.models import Brands, Category, CategorySite


def product_filters_data():
    brands, categories, site_categories = [Brands.objects.filter(active=True), 
                                          Category.objects.all(),
                                          CategorySite.objects.filter(active=True)
                                          ]
    return [brands, categories, site_categories]


def product_filters_get(request):
    search_name = request.GET.get('search_name', None)
    brand_name = request.GET.getlist('brand_name', None)
    category_name = request.GET.getlist('category_name', None)
    category_site_name = request.GET.getlist('category_site_name', None)
    return [search_name, brand_name, category_name,category_site_name]