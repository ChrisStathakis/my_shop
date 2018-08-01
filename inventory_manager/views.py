from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, FormView, CreateView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger


from products.models import Product,  Color, Size
from products.forms import VendorForm
from .models import Order, OrderItem, Vendor, Category
from .models import PaymentOrders
from site_settings.forms import PaymentForm
from inventory_manager.models import Order, OrderItem, Vendor
from inventory_manager.forms import OrderQuickForm, VendorQuickForm, WarehouseOrderForm, OrderItemForm

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
    products = queryset.filter(size=False)
    products_with_size = queryset.filter(size=True)
    form = WarehouseOrderForm(instance=instance)
    if 'add_products' in request.GET:
        ids = request.GET.getlist('ids', None)
        if ids:
            for id in ids:
                get_product = get_object_or_404(Product, id=id)
                OrderItem.add_to_order(request, product=get_product, order=instance)
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
def update_warehouse(pk, action):
    instance = get_object_or_404(Order, id=pk)
    instance.update_warehouse(action)
    return HttpResponseRedirect(reverse('inventory:warehouse_order_detail'), kwargs={'dk': instance.id})


@staff_member_required
def warehouse_add_order_item(request, dk, pk):
    instance = get_object_or_404(Product, id=pk)
    order = get_object_or_404(Order, id=dk)
    form = OrderItemForm(request.POST or None, initial={'product': instance,
                                                        'order': order,
                                                        'qty': 1,
                                                        'price': instance.price_buy,
                                                        'discount': instance.order_discount,
                                                        })
    if form.is_valid():
        get_product = form.cleaned_data.get('product', None)
        get_order = form.cleaned_data.get('order', None)
        exists = OrderItem.objects.filter(order=get_order, product=get_product) if get_order and get_product else None
        if exists:
            current_item = exists.first()
            qty = form.cleaned_data.get('qty', None)
            current_item.qty += int(qty)
            current_item.save()
        else:
            new_item = form.save()
        return HttpResponseRedirect(reverse('dashboard:warehouse_order_detail', kwargs={'dk': dk}))
    page_title = 'Add product %s' % instance
    context = locals()
    return render(request, 'dash_ware/form.html', context)


@staff_member_required
def edit_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    form = OrderItemForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:warehouse_order_detail', kwargs={'dk': instance.order.id}))
    context = locals()
    return render(request, 'dash_ware/form.html', context)


@staff_member_required
def delete_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:warehouse_order_edit', kwargs={'dk': instance.order.id}))



@method_decorator(staff_member_required, name='dispatch')
class WarehouseHomepage(TemplateView):
    template_name = 'inventory_manager/'

    def get_context_data(self, **kwargs):
        context = super(WarehouseHomepage, self).get_context_data(**kwargs)

        context.update(locals())
        return context


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
    template_name = 'dash_ware/form.html'
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
    model = Order
    template_name = 'inventory_manager/payment_list.html'

    def get_queryset(self):
        queryset = Order.objects.all()
        queryset = self.model.filter_data(self.request, queryset)
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
    template_name = 'dash_ware/form.html'
    model = PaymentOrders
    form_class = PaymentForm

    def get_initial(self):
        initial = super(WarehousePaymentOrderCreate, self).get_initial()
        instance = get_object_or_404(Supply, id=self.kwargs['pk'])
        initial['object_id'] = instance.id
        initial['content_type'] = ContentType.objects.get_for_model(instance)
        initial['date_expired'] = datetime.datetime.now()
        initial['title'] = '%s' % instance.title
        initial['is_expense'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentOrderCreate, self).get_context_data(**kwargs)
        title = 'Create Check'
        back_url = ''
        context.update(locals())
        return context

    def form_valid(self, form):
        if form.is_valid():
            print('works!')
            form.save()
            messages.success(self.request, 'The check created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@staff_member_required
def edit_check_order(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    form = PaymentForm(request.POST or None, instance=instance, initial={'is_expense': True})
    if form.is_valid():
        form.save()
        messages.success(request, 'The Check order is edited')
        return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id }))
    print(form.errors)
    page_title = 'Edit %s' % instance.title
    context = locals()
    return render(request, 'dash_ware/form.html', context)


    def get_success_url(self):
        instance = get_object_or_404(PaymentOrders, id=self.kwargs['pk'])
        return reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id })


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
