from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from .models import RetailOrder, RetailOrderItem
from products.models import Product


@staff_member_required()
def ajax_products_search(request, pk):
    data = dict()
    order = get_object_or_404(RetailOrder, id=pk)
    is_sale = True if order.order_type == 'r' else False
    search_name = request.GET.get('search_name', None)
    products = Product.objects.none()
    if search_name:
        products = Product.my_query.active()
        products = Product.filters_data(request, products)
    print(products.count())
    data['products'] = render_to_string(request=request,
                                        template_name='PoS/ajax/products_search.html',
                                        context={'object_list': products,
                                                 'instance': order,
                                                 'is_sale': is_sale
                                                 }
                                        )

    return JsonResponse(data)


@staff_member_required
def ajax_edit_order_item(request, pk, qty, action):
    data = dict()
    order_item = get_object_or_404(RetailOrderItem, id=pk)
    instance = order_item.order
    order_item.create_or_edit_item(order_item.order, order_item.title, qty, action)
    instance.refresh_from_db()
    data['order_items_section'] = render_to_string(template_name='PoS/ajax/order_items.html',
                                                  request=request,
                                                  context={'instance': instance}
                                                  )
    data['final_value'] = render_to_string(template_name='PoS/ajax/final_value.html',
                                           request=request,
                                           context={'instance': instance}
                                           )
    return JsonResponse(data)


def ajax_add_product(request, pk, dk):
    print('add works!')
    data = {}
    instance = get_object_or_404(RetailOrder, id=pk)
    product = get_object_or_404(Product, id=dk)
    RetailOrderItem.create_or_edit_item(instance, product, 1, 'ADD')
    instance.refresh_from_db()
    data['order_items_section'] = render_to_string(template_name='PoS/ajax/order_items.html',
                                                   request=request,
                                                   context={'instance': instance}
                                                   )
    data['final_value'] = render_to_string(template_name='PoS/ajax/final_value.html',
                                           request=request,
                                           context={'instance': instance}
                                           )
    return JsonResponse(data)
