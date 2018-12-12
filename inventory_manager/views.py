from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, FormView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.forms import inlineformset_factory
from django.contrib.contenttypes.models import ContentType

from products.models import Product,  Color, Size, SizeAttribute
from products.forms import VendorForm, CreateProductForm
from .models import Order, OrderItem, Vendor, Category, WarehouseOrderImage
from .models import PaymentOrders
from .forms import OrderItemSizeForm, OrderItemForm, WarehouseOrderImageForm, StockForm
from site_settings.forms import PaymentForm
from site_settings.tools import dashboard_filters_name
from inventory_manager.models import Order, OrderItem, Vendor, Stock, StockItem
from inventory_manager.forms import OrderQuickForm, VendorQuickForm, WarehouseOrderForm, OrderItemForm, OrderItemSize

import datetime
import decimal


@method_decorator(staff_member_required, name='dispatch')
class WareHouseOrderPage(ListView):
    template_name = 'inventory_manager/index.html'
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.all()
        queryset = self.model.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WareHouseOrderPage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        date_start = self.request.GET.get('date_start', None)
        date_end = self.request.GET.get('date_end', None)
        vendors = Vendor.objects.filter(active=True)
        context.update(locals())
        return context


@staff_member_required
def create_new_warehouse_order(request):
    form = OrderQuickForm(request.POST or None,
                          initial = {'date_expired': datetime.datetime.now()}
                          )
    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    context = locals()
    return render(request, 'inventory_manager/create_order.html', context)


@staff_member_required
def quick_vendor_create(request):
    form = VendorQuickForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_vendor");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@staff_member_required
def warehouse_order_detail(request, dk):
    instance = get_object_or_404(Order, id=dk)
    queryset = Product.my_query.get_site_queryset().active_warehouse().filter(vendor=instance.vendor)
    if 'search_name' in request.GET:
        queryset = queryset.filter(title__icontains=request.GET.get('search_name', None))
    products = queryset[:10]
    products_with_size = queryset.filter(size=True)
    # forms
    form_product = CreateProductForm()
    form = WarehouseOrderForm(instance=instance)
    form_image = WarehouseOrderImageForm(initial={'order_related': instance})
    form_payment = PaymentForm(initial={'payment_method': instance.payment_method,
                                        'value': instance.get_remaining_value,
                                        'title': f'{instance.title}',
                                        'date_expired': datetime.datetime.now(),
                                        'is_paid': True,
                                        'is_expense': True,
                                        'object_id': dk,
                                        'content_type': ContentType.objects.get_for_model(Order)
                                        })
    if 'payment' in request.POST:
        form_payment = PaymentForm(request.POST)
        if form_payment.is_valid():
            form_payment.save()
            instance.save()
            return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    if 'image' in request.POST:
        form_image = WarehouseOrderImageForm(request.POST, request.FILES, initial={'order_related': instance})
        if form_image.is_valid():
            form_image.save()
            return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    if 'add_products' in request.POST:
        ids = request.POST.getlist('add_', [])
        for id in ids:
            get_product = get_object_or_404(Product, id=id)
            OrderItem.add_to_order(request, product=get_product, order=instance)
        instance.save()
        return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    if 'create_product' in request.POST:
        form_product = CreateProductForm(request.POST)
        if form_product.is_valid():
            new_product = form_product.save(commit=False)
            new_product.vendor = instance.vendor
            new_product.save()
            return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    if request.POST:
        form = WarehouseOrderForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'The order Edited!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    return render(request, 'inventory_manager/order_detail.html', context)


@staff_member_required
def order_add_sizechart(request, pk, dk):
    instance = get_object_or_404(Order, id=pk)
    product = get_object_or_404(Product, id=dk)
    order_item, created = OrderItem.objects.get_or_create(order=instance,
                                                          product=product,
                                                          )
    sizes = Size.objects.all()
    if request.POST:
        price = request.POST.get('price', None)
        discount = request.POST.get('discount', None)
        order_item.value = price
        if discount:
            order_item.discount_value = discount
        order_item.save()
        id_list = request.POST.getlist('ids', [])
        for id in id_list:
            size = get_object_or_404(Size, id=int(id))
            qty_ = request.POST.get(f'qty_{id}', None)
            product_size, created = SizeAttribute.objects.get_or_create(title=size,
                                                                        product=order_item.product
                                                                        )
            order_size, size_created = OrderItemSize.objects.get_or_create(order_item_related=order_item,
                                                                      size_related=size
                                                                      )
            if size_created:
                order_size.product_attr_related = product_size
            order_size.qty += int(qty_)
            order_size.value = price
            order_item.discount = discount
            order_item.save()
        return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    content = locals()
    return render(request, 'inventory_manager/order/size_chart.html', content)


@staff_member_required
def order_edit_sizechart(request, pk):
    edit, instance_ = True, get_object_or_404(OrderItem, id=pk)
    instance, product, instance_sizes, initial = instance_.order, instance_.product, instance_.attributes.all(), []
    for size in instance_sizes:
        initial.append({'order_item_related': size.order_item_related,
                        'size_related': size.size_related,
                        'qty': size.qty,
                        'value': size.value }
                )
    order_item_form = OrderItemForm(instance=instance_)
    OrderItemSizeFormSet = inlineformset_factory(OrderItem, OrderItemSize, extra=0, form=OrderItemSizeForm)
    formset = OrderItemSizeFormSet(instance=instance_)

    if 'order_item' in request.POST:
        order_item_form = OrderItemForm(request.POST, instance=instance_)
        if order_item_form.is_valid():
            order_item_form.save()
            return HttpResponseRedirect(reverse('inventory:order_edit_sizechart', kwargs={'pk': pk}))
    
    if request.POST:
        formset = OrderItemSizeFormSet(request.POST, initial=initial, instance=instance_)
        
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.id}))
    content = locals()
    return render(request, 'inventory_manager/order/size_chart.html', content)


@staff_member_required
def delete_warehouse_image(request, pk):
    instance = get_object_or_404(WarehouseOrderImage, id=pk)
    order = instance.order_related
    instance.delete()
    return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': order.id}))


@staff_member_required
def order_update_warehouse(request, pk):
    instance = get_object_or_404(Order, id=pk)
    instance.save()
    return HttpResponseRedirect(reverse('inventory:warehouse_order_detail'), kwargs={'dk': pk})


@staff_member_required
def edit_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    page_title = f'Edit {instance.product.title}'
    back_url = reverse('inventory:warehouse_order_detail', kwargs={'dk':instance.order.id})
    old_qty = instance.qty
    form = OrderItemForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance.remove_from_order(old_qty)
        new_qty = request.POST.get('qty')
        form.save()
        instance.quick_add_to_order(new_qty)
        return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.order.id}))
    context = locals()
    return render(request, 'inventory_manager/form.html', context)


@staff_member_required
def delete_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.order.id}))


@staff_member_required
def ajax_search_products(request):
    data = {}
    search_name, instance_id = request.GET.get('search_name', None), request.GET.get('instance_id', None)
    instance = get_object_or_404(Order, id=instance_id)
    vendor = instance.vendor
    queryset = Product.my_query.active().filter(vendor=vendor)
    queryset = Product.filters_data(request, queryset)[:10]
    data['results'] = render_to_string(template_name='inventory_manager/ajax/product_container.html',
                                      request=request,
                                      context={'products': queryset, 'instance': instance}
                                      )
    return JsonResponse(data)


@staff_member_required
def order_payment_manager_edit_or_remove(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    form = PaymentForm(instance=instance, initial={'is_expense': True})
    if request.POST:
        form = PaymentForm(request.POST, instance=instance, initial={'is_expense': True})
        if form.is_valid():
            form.save()
            instance.content_object.save()
            return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': instance.object_id}))
    page_title = f'Edit {instance.title} payment'
    back_url = ''
    return render(request, 'inventory_manager/form.html', context=locals())


@staff_member_required
def order_delete_payment(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    order = instance.content_object
    instance.delete()
    order.save()
    return HttpResponseRedirect(reverse('inventory:warehouse_order_detail', kwargs={'dk': order.id}))


@method_decorator(staff_member_required, name='dispatch')
class VendorPageList(ListView):
    template_name = 'inventory_manager/vendor_list.html'
    model = Vendor
    paginate_by = 10

    def get_queryset(self):
        queryset = Vendor.objects.all()
        queryset = self.model.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VendorPageList, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        balance_name = self.request.GET.get('balance_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class VendorPageDetail(UpdateView):
    template_name = 'inventory_manager/vendor_detail.html'
    form_class = VendorForm
    model = Vendor

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@method_decorator(staff_member_required, name='dispatch')
class VendorPageCreate(FormView):
    template_name = 'dashboard/page_create.html'
    form_class = VendorForm

    def get_context_data(self, **kwargs):
        context = super(VendorPageCreate, self).get_context_data(**kwargs)
        page_title, back_url = 'Create Vendor', reverse('inventory:vendor_create')
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New Vendor Added!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@method_decorator(staff_member_required, name='dispatch')
class WarehousePaymentPage(ListView):
    model = PaymentOrders
    template_name = 'inventory_manager/payment_list.html'

    def get_queryset(self):
        queryset = PaymentOrders.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentPage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        paid_name = self.request.GET.get('paid_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        date_start = self.request.GET.get('date_start', None)
        date_end = self.request.GET.get('date_end', None)
        vendors  = Vendor.objects.filter(active=True)
        context.update(locals())
        return context


@staff_member_required
def warehouse_order_paid(request, pk):
    instance = get_object_or_404(Order, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The order %s is paid.')
    return HttpResponseRedirect(reverse('inventory:payment_list'))


@staff_member_required
def warehouser_order_paid_detail(request, pk):
    instance = get_object_or_404(Order, id=pk)
    vendor = instance.vendor
    create = True
    form = PaymentForm(request.POST or None, initial={'value': instance.get_remaining_value,
                                                      'content_type': ContentType.objects.get_for_model(instance),
                                                      'payment_type': instance.payment_method,
                                                      'title': '%s' % instance.code,
                                                      'date_expired': instance.date_created,
                                                      'object_id': pk,
                                                      'is_expense': True,
                                                      'is_paid':True,
                                                      })
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The payment added!')
            return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': pk}))
    context = locals()
    return render(request, 'inventory_manager/payment_details.html', context)


@staff_member_required
def warehouse_check_order_convert(request, dk, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    order = get_object_or_404(Order, id=dk)
    if instance.value <= order.total_price:
        instance.object_id = dk
        instance.content_type = ContentType.objects.get_for_model(order)
        instance.is_paid = True
        instance.save()
    else:
        new_payment_order = PaymentOrders.objects.create(content_type=ContentType.objects.get_for_model(order),
                                                         object_id=dk,
                                                         title='%s' % order.code,
                                                         date_expired=instance.date_expired,
                                                         payment_type=instance.payment_type,
                                                         bank=instance.bank,
                                                         value=order.total_price,
                                                         is_expense=True,
                                                         is_paid=True
                                                         )
        instance.value -= order.total_price
        instance.save()
    messages.success(request, 'The check order is converted')
    return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': dk}))


@staff_member_required
def warehouse_order_paid_delete(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.delete()
    messages.warning(request, 'The payment deleted!')
    return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': instance.object_id}))


@staff_member_required
def warehouse_edit_paid_order(request, dk, pk):
    instance = get_object_or_404(Order, id=dk)
    payorder = get_object_or_404(PaymentOrders, id=pk)
    form = PaymentForm(request.POST or None,
                       instance=payorder,
                       initial={'is_expense': True
                                })
    create = False
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The paid order is edited')
            return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail',
                                                kwargs={'pk': instance.id}
                                                )
                                        )
    context = locals()
    return render(request, 'inventory_manager/form_edit_payment_order.html', context)


@method_decorator(staff_member_required, name='dispatch')
class WarehousePaymentOrderCreate(CreateView):
    template_name = 'inventory_manager/form.html'
    model = PaymentOrders
    form_class = PaymentForm

    def get_initial(self):
        initial = super(WarehousePaymentOrderCreate, self).get_initial()
        instance = get_object_or_404(Vendor, id=self.kwargs['pk'])
        initial['object_id'] = instance.id
        initial['content_type'] = ContentType.objects.get_for_model(instance)
        initial['date_expired'] = datetime.datetime.now()
        initial['title'] = '%s' % instance.title
        initial['is_expense'] = True
        initial['value'] = instance.balance
        initial['is_check'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentOrderCreate, self).get_context_data(**kwargs)
        page_title = 'Create Check'
        back_url = reverse('inventory:vendor_list')
        context.update(locals())
        return context

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            instance = get_object_or_404(Vendor, id=self.kwargs['pk'])
            instance.save()
            messages.success(self.request, 'The check created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@staff_member_required
def edit_check_order(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    back_url = reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id})
    form = PaymentForm(request.POST or None, instance=instance, initial={'is_expense': True})
    if form.is_valid():
        form.save()
        messages.success(request, 'The Check order is edited')
        return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id }))
    print(form.errors)
    page_title = 'Edit %s' % instance.title
    context = locals()
    return render(request, 'inventory_manager/form.html', context)


@staff_member_required
def delete_check_order(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.delete()
    messages.warning(request, 'The Payment Order deleted!')
    return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id}))


@staff_member_required
def check_order_paid(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The order is paid.')
    return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id}))


@method_decorator(staff_member_required, name='dispatch')
class CheckOrdersView(ListView):
    template_name = 'inventory_manager/checkOrders.html'
    model = PaymentOrders
    paginate_by = 100

    def get_queryset(self):
        queryset = PaymentOrders.objects.filter(is_check=True)
        vendors = Vendor.objects.all()
        vendors = Vendor.filter_data(self.request, vendors)
        vendors_ids = vendors.values_list('id', flat=True)
        content_type_model = ContentType.objects.get_for_model(Vendor)
        queryset = queryset.filter(object_id__in=vendors_ids, content_type=content_type_model)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CheckOrdersView, self).get_context_data(**kwargs)
        vendors = Vendor.objects.filter(active=True)
        date_start, date_end, search_name = dashboard_filters_name(self.request)
        vendor_name, paid_name = [self.request.GET.getlist('vendor_name', None),
                                  self.request.GET.get('check_name', None)
                                ]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CheckOrderUpdateView(UpdateView):
    model = PaymentOrders
    template_name = 'inventory_manager/form.html'
    form_class = PaymentForm
    success_url = reverse_lazy('inventory:check_orders')

    def get_initial(self):
        initial = super(CheckOrderUpdateView, self).get_initial()
        instance = get_object_or_404(PaymentOrders, id=self.kwargs['pk'])
        initial['object_id'] = instance.id
        initial['content_type'] = instance.content_type
        initial['is_expense'] = instance.is_expense
        return initial

    def get_context_data(self, **kwargs):
        context = super(CheckOrderUpdateView, self).get_context_data(**kwargs)
        back_url = self.success_url
        page_title = 'Edit Payment'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Payment is edited')
        return super().form_valid(form)



@method_decorator(staff_member_required, name='dispatch')
class StockListView(ListView, FormView):
    model = Stock
    template_name = 'inventory_manager/stock_list_page.html'
    queryset = Stock.objects.all()
    form_class = StockForm

    def form_valid(self, form):
        form.save()
        super(StockListView, self).form_valid(form)

    def get_success_url(self):
        new_id = Stock.objects.last().id
        return reverse('')

@staff_member_required
def stock_detail_view(request, pk):
    pass
    form = ';'
