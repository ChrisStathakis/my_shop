from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, FormView
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.db.models import Q
from django.contrib import messages
from django.db.models import Avg, Sum
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import json

import datetime
from accounts.models import CostumerAccount, User
from .models import RetailOrder, RetailOrderItem
from .forms import SalesForm
from products.models import Product, SizeAttribute

from site_settings.forms import PaymentForm


# Retail Pos

@method_decorator(staff_member_required, name='dispatch')
class HomePage(ListView):
    template_name = 'PoS/homepage.html'
    model = RetailOrder

    def get_queryset(self):
        queryset = RetailOrder.objects.filter(order_type__in=['r', 'b'])
        return queryset


@staff_member_required()
def create_new_sales_order(request):
    id = RetailOrder.objects.count() + 1 if RetailOrder.objects.all().exists() else 0 + 1
    title = f'Retail Order {id}'
    payment, costumer = RetailOrder.new_order_payment_and_costumer()
    user = request.user
    new_order = RetailOrder.objects.create(title=title,
                                           user_account=request.user,
                                           payment_method=payment,
                                           costumer_account=costumer,
                                           order_type='r'
                                           )
    new_order.save()
    return HttpResponseRedirect(reverse('POS:sales', kwargs={'pk': new_order.id}))


@staff_member_required
def create_return_order(request, pk):
    order = get_object_or_404(RetailOrder, id=pk)
    new_order = RetailOrder.objects.create(order_related=order,
                                           title=f'Return order',
                                           order_type='b'
                                           )
    items = RetailOrderItem.objects.filter(order=order)
    if items:
        for item in items:
            new_item = RetailOrderItem.objects.create(order=new_order,
                                                      title=item.title,
                                                      cost=item.cost,
                                                      price=item.price,
                                                      qty=item.qty,
                                                      discount=item.discount

                                                      )


@staff_member_required
def create_eshop_order(request):
    user = request.user
    new_order = RetailOrder.objects.create(order_type='e')
    if user:
        new_order.user_account = user
    new_order.save()
    return HttpResponseRedirect('/point-of-sale/sales/%s' % new_order.id)


@staff_member_required
def sales(request, pk):
    object_list = Product.my_query.active_with_qty()
    instance = get_object_or_404(RetailOrder, id=pk)
    form = SalesForm(instance=instance)
    search_name = request.GET.get('search_name', None)
    barcode = request.GET.get('barcode', None)
    object_list = object_list.filter(Q(title__icontains=search_name) |
                                     Q(sku__icontains=search_name)
                                     ).distinct() if search_name else object_list
    if barcode:
        RetailOrderItem.barcode(request, instance)
    if request.POST:
        form = SalesForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': pk}))
        form_paid = PaymentForm(request.POST)
        if form_paid.is_valid():
            form_paid.save()
            return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': pk}))
    object_list = object_list[:10]
    context = locals()
    return render(request, 'PoS/sales.html', context)


@staff_member_required
def add_product_to_order_(request, dk, pk, qty=1):
    instance = get_object_or_404(RetailOrder, id=dk)
    product = get_object_or_404(Product, id=pk)
    RetailOrderItem.create_or_edit_item(instance, product, qty, 'ADD')
    if instance.order_type in ['wa', 'wr']:
        return HttpResponseRedirect(reverse('POS:warehouse_in', kwargs={'dk': dk}))
    return HttpResponseRedirect(reverse('POS:sales', kwargs={'pk': dk}))


@staff_member_required
def edit_product_item_view(request, pk, qty, type):
    instance = get_object_or_404(RetailOrderItem, id=pk)
    RetailOrderItem.create_or_edit_item(instance.order, instance.title, qty, type)
    return HttpResponseRedirect(reverse('POS:sales', kwargs={'pk': instance.order.id}))


@staff_member_required
def delete_order_view(request, dk):
    instance = get_object_or_404(RetailOrder, id=dk)
    instance.delete()
    messages.warning(request, 'The Retail Order Deleted!')
    return HttpResponseRedirect(reverse('POS:homepage'))


@staff_member_required
def retail_order_done(request, pk):
    instance = get_object_or_404(RetailOrder, id=pk)
    if not instance.order_items.all():
        instance.delete()
        return HttpResponseRedirect(reverse('POS:homepage'))
    instance.is_paid = True
    instance.status = '8'
    instance.save()
    return HttpResponseRedirect(reverse('POS:homepage'))


#  actions


@staff_member_required()
def order_paid(request, pk):
    order = get_object_or_404(RetailOrder, id=pk)
    order.is_paid = True
    order.save()
    messages.success(request, 'Payment Added!')
    return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': pk}))


@staff_member_required
def delete_payment_order(request, dk, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    order = get_object_or_404(RetailOrder, id=dk)
    order.is_paid = False
    order.status = '2'
    order.save()
    instance.delete()
    messages.warning(request, 'Payment order deleted!')
    return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': dk}))




def AuthorCreatePopup(request):
    form = CreateCostumerPosForm(request.POST or None)
    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form

        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_costumer_account");</script>' % (instance.pk, instance))

    return render(request, "PoS/popup/costumer_form.html", {"form": form})


def AuthorEditPopup(request, pk=None):
    instance = get_object_or_404(CostumerAccount, pk=pk)
    form = CreateCostumerPosForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form

        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))

    return render(request, "PoS/popup/costumer_form.html", {"form": form})


@csrf_exempt
def get_author_id(request):
    if request.is_ajax():
        author_name = request.GET['author_name']
        author_id = CostumerAccount.objects.get(name=author_name).id
        data = {'author_id': author_id, }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")


def ajax_payment_add(request, pk):
    data = dict()
    get_order = get_object_or_404(RetailOrder, id=pk)
    form = PaymentForm(initial={'payment_type': get_order.payment_method,
                                'is_expense': False,
                                'is_paid': True,
                                'date_expired': datetime.datetime.now(),
                                'title': 'Αποπληρωμή %s' % get_order,
                                'value': get_order.final_price - get_order.paid_value,
                                'content_type': ContentType.objects.get_for_model(RetailOrder),
                                'object_id': pk
                                })
    data['add_payment'] = render_to_string(request=request,
                                           template_name='PoS/ajax/payment.html',
                                           context=locals()
                                           )
    return JsonResponse(data)
