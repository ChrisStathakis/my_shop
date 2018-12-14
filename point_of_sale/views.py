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
from site_settings.tools import initial_date

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
def cancel_or_delete_order(request, pk):
    instance = get_object_or_404(RetailOrder, id=pk)
    for order_item in instance.order_items.all():
        order_item.delete()
    for payment in instance.payorders.all():
        payment.delete()
    instance.delete()
    return HttpResponseRedirect(reverse('POS:homepage'))


@staff_member_required
def retail_order_done(request, pk):
    instance = get_object_or_404(RetailOrder, id=pk)
    instance.create_check()
    instance.status = '8'
    instance.save()
    return HttpResponseRedirect(reverse('POS:homepage'))


@staff_member_required
def retail_order_unlock(request, pk):
    instance = get_object_or_404(RetailOrder, id=pk)
    for payment in instance.payorders.all():
        payment.delete()
    instance.is_paid = False
    instance.save()
    return HttpResponseRedirect(reverse('POS:sales', kwargs={'pk': instance.id}))


@method_decorator(staff_member_required, name='dispatch')
class HomepageRetailReturnOrder(ListView):
    model = RetailOrder
    template_name = 'PoS/return_section/homepage_return.html'

    def get_queryset(self):
        date_start, date_end, date_range = initial_date(self.request)
        queryset = RetailOrder.my_query.get_queryset().returns(date_start, date_end)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomepageRetailReturnOrder, self).get_context_data(**kwargs)
        date_start, date_end, date_range = initial_date(self.request)
        retail_orders = RetailOrder.my_query.sells_orders(date_start, date_end)
        context.update(locals())
        return context


@staff_member_required
def create_order_return_from_order_view(request, pk):
    instance = get_object_or_404(RetailOrder, id=pk)
    return_instance, created = RetailOrder.objects.get_or_create(order_type='b',
                                                        order_related=instance
                                                        )
    for order_item in instance.order_items.all():
        new_order_item = order_item
        new_order_item.pk = None
        new_order_item.order = return_instance
        new_order_item.is_return = True
        new_order_item.save()
    return_instance.refresh_from_db()
    return HttpResponseRedirect(reverse('POS:sales', kwargs={'pk': return_instance.id}))
