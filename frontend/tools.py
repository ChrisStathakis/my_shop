from products.models import Color, Size, Product, SizeAttribute
from .models import CategorySite, Brands
from django.shortcuts import HttpResponse, HttpResponseRedirect


def initial_filter_data(queryset):
    brands_id = queryset.values_list('brand', flat=False)
    brands = Brands.objects.filter(id__in=brands_id)
    categories_id = queryset.values_list('category_site', flat=False)
    categories = CategorySite.objects.filter(id__in=categories_id)
    color_id = queryset.values_list('color', flat=True)
    colors = Color.objects.filter(id__in=color_id)
    sizes = SizeAttribute.objects.filter(product_related__in=queryset).values_list('title', 'title__title').distinct()
    print(sizes)
    return [brands, categories, colors, sizes]


def grab_user_filter_data(request):
    brand_name = request.GET.getlist('brand_name')
    category_name = request.GET.getlist('site_cate_name')
    color_name = request.GET.getlist('color_name')
    return [brand_name, category_name, color_name]


def queryset_ordering(request, queryset,):
    ordering_list = {'1': '-price',
                     '2': 'title',
                     '3': '-id'
                     }
    choice = request.GET.get('order_by', None)
    order_choice = ordering_list.get(choice, None) if choice else None
    queryset = queryset.order_by('%s' % order_choice) if order_choice else queryset
    return queryset


