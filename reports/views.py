from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
from django.db.models import ExpressionWrapper, DecimalField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.context_processors import csrf
from django.views.generic import ListView, DetailView, TemplateView
from products.models import *
from point_of_sale.models import *
from transcations.models import *
from inventory_manager.models import Vendor, Order, OrderItem
from site_settings.models import PaymentOrders
from site_settings.constants import *
from accounts.models import CostumerAccount
from .tools import (get_filters_data_payments, get_filters_data_warehouse_invoices, initial_data_invoices,
                    initial_data_from_database, warehouse_filters, estimate_date_start_end_and_months,
                    warehouse_vendors_analysis, get_filters_data, balance_sheet_chart_analysis, filter_date
                    )


from itertools import chain
from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class HomepageReport(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageReport, self).get_context_data(**kwargs)
        retail_orders = RetailOrder.objects.all().order_by('-timestamp')[:10]
        warehouse_orders = Order.objects.all().order_by('-date_expired')[:10]
        paid_orders = PaymentOrders.objects.all()[:10]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class HomepageProductWarning(ListView):
    model = Product
    template_name = 'report/homepage/product_warning.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(qty__lte=0, active=True)
        return queryset[:30]

    def get_content_data(self, **kwargs):
        context = super(HomepageProductWarning, self).get_content_data(**kwargs)
        products_with_sizes = SizeAttribute.objects.filter(qty__lte=0, active=True)[:30]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ReportProducts(ListView):
    template_name = 'report/warehouse/products.html'
    model = Product
    paginate_by = 100

    def get_queryset(self):
        queryset = Product.my_query.active_for_site()
        queryset = Product.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ReportProducts, self).get_context_data(**kwargs)
        currency = CURRENCY
        vendors, categories, categories_site, colors, sizes, brands = initial_data_from_database()
        product_count_qty, product_count = (self.object_list.aggregate(Sum('qty'))['qty__sum'] if self.object_list else 0,
                                            self.object_list.count()
                                            )
        search_name, cate_name, vendor_name, brand_name, category_site_name, site_status, color_name, size_name, \
        discount_name, qty_name = get_filters_data(self.request)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductSizeView(ListView):
    model = Product
    template_name = 'report/warehouse/products_with_size.html'
    paginate_by = 100

    def get_queryset(self):
        queryset = Product.my_query.active_warehouse_with_attr()
        queryset = Product.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductSizeView, self).get_context_data(**kwargs)
        vendors, categories, categories_site, colors, sizes, brands = initial_data_from_database()
        search_name, category_name, vendor_name, brand_name, category_site_name, site_status, color_name, size_name, \
        discount_name, qty_name = get_filters_data(self.request)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductDetail(LoginRequiredMixin, DetailView):
    template_name = 'report/warehouse/products_id.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        date_pick, currency = self.request.GET.get('date_pick'), CURRENCY
        date_end = date_end + relativedelta(days=1)
        order_items = OrderItem.objects.filter(product=self.object,
                                               order__date_expired__range=[date_start, date_end]
                                               )
        order_items_analysis = order_items.values('product').annotate(total_clean=Sum('total_clean_value'),
                                                                      total_tax=Sum('total_value_with_taxes',
                                                                      output_field=models.FloatField()),
                                                                      qty_count=Sum('qty'),
                                                                    )
        # retail orders
        retail_items_all = RetailOrderItem.objects.filter(title=self.object,
                                                          order__date_expired__range=[date_start, date_end]
                                                          )
        retail_items = retail_items_all.filter(order__order_type__in=['r', 'e','wa'])
        retail_items_analysis = retail_items.values('title').annotate(total_incomes=Sum(F('qty')*F('final_value'),
                                                                      output_field=models.FloatField()),
                                                                      total_qty=Sum('qty'),
                                                                    ).order_by('title')
        return_products = retail_items_all.filter(order__order_type__in=['b', 'd'])
        return_products_analysis = return_products.values('title').annotate(total_incomes=Sum(F('qty')*F('final_value'),
                                                                            output_field=models.FloatField()),
                                                                            total_qty=Sum('qty'),
                                                                            ).order_by('title')
        win_or_loss = retail_items_analysis[0]['total_incomes'] if retail_items_analysis else 0 - \
                      order_items_analysis[0]['total_tax'] if order_items_analysis else 0 - \
                      return_products_analysis[0]['total_incomes'] if return_products_analysis else 0
        win_or_loss = round(win_or_loss, 2)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BrandsPage(ListView):
    template_name = 'report/brandsPage.html'
    model = Brands
    paginate_by = 20

    def get_queryset(self):
        queryset = Brands.objects.filter(active=True)
        queryset = Brands.filters_data(queryset, self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrandsPage, self).get_context_data(**kwargs)
        search_name, category_name, vendor_name, brand_name, category_site_name, site_status, color_name, size_name, \
        discount_name, qty_name = get_filters_data(self.request)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BrandDetailView(DetailView):
    template_name = 'report/brands_detail_view.html'
    model = Brands

   
@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoriesView(ListView):
    model = Category
    template_name = 'report/warehouse/category_report.html'
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super(WarehouseCategoriesView, self).get_context_data(**kwargs)
        title = 'Warehouse Categories'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoryView(DetailView):
    model = Category
    template_name = 'report/details/warehouse_category.html'

    def get_context_data(self, **kwargs):
        context = super(WarehouseCategoryView, self).get_context_data(**kwargs)
        products = Product.objects.filter(category=self.object)
        total_qty = products.aggregate(total_qty=Sum('qty')) if products else 0
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoriesSiteView(ListView):
    model = CategorySite
    template_name = 'report/warehouse/category_report.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        content = super(CategoriesSiteView, self).get_context_data(**kwargs)
        title = 'Categories Site'

        content.update(locals())
        return content


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteView(DetailView):
    model = CategorySite
    template_name = ''


@method_decorator(staff_member_required, name='dispatch')
class WarehouseOrderView(ListView):
    template_name = 'report/warehouse/orders.html'
    model = Order
    paginate_by = 50

    def get_queryset(self):
        date_start, date_end = filter_date(self.request)
        queryset = Order.my_query.filter_by_date(date_start, date_end)
        queryset = Order.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        date_start, date_end = filter_date(self.request)
        orders, currency = self.object_list, CURRENCY
        vendors, payment_method, order_types = initial_data_invoices()

        vendor_name, order_type_name = get_filters_data_warehouse_invoices(self.request)
        payment_name, is_paid_name = get_filters_data_payments(self.request)
        order_count, total_value, paid_value = orders.count(), orders.aggregate(Sum('final_value'))[
            'final_value__sum'] \
            if orders else 0, orders.aggregate(Sum('paid_value'))[
                                                   'paid_value__sum'] if orders else 0
        diff = total_value - paid_value
        warehouse_analysis = balance_sheet_chart_analysis(date_start, date_end, orders, 'final_value')
        warehouse_vendors = orders.values('vendor__title').annotate(value_total=Sum('final_value'),
                                                                    paid_val=Sum('paid_value')
                                                                    ).order_by('-value_total')
        content.update(locals())
        return content


@method_decorator(staff_member_required, name='dispatch')
class WarehouseDetailView(DetailView):
    model = Order
    template_name = 'report/warehouse/orders_id.html'


@method_decorator(staff_member_required, name='dispatch')
class VendorsPage(ListView):
    model = Vendor
    template_name = 'report/warehouse/vendors_list.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Vendor.objects.all()
        queryset = Vendor.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VendorsPage, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        date_start_last_year, date_end_last_year = date_start- relativedelta(year=1), date_end-relativedelta(year=1)
        date_pick, currency = self.request.GET.get('date_pick'), CURRENCY
        vendor_name, balance_name, search_name = [self.request.GET.getlist('vendor_name'),
                                                  self.request.GET.get('balance_name'),
                                                  self.request.GET.get('search_name'),
                                                 ]

        vendors = self.object_list
        orders = Order.objects.filter(timestamp__range=[date_start, date_end])
        chart_data = [Vendor.objects.all().aggregate(Sum('balance'))['balance__sum'] if Vendor.objects.all() else 0,
                      orders.aggregate(Sum('final_value'))['final_value__sum'] if orders else 0,
                      orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
                  ]
        analysis = warehouse_vendors_analysis(self.request, date_start, date_end)
        analysis_last_year = warehouse_vendors_analysis(self.request, date_start_last_year, date_end_last_year)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class VendorDetailReportView(ListView):
    template_name = 'report/warehouse/vendor_detail.html'
    model = Order

    def get_queryset(self):
        self.object = get_object_or_404(Vendor, id=self.kwargs['pk'])
        queryset = Order.objects.filter(vendor=self.object)
        return queryset

    def get_context_data(self, **kwargs):
        content = super(VendorDetailReportView, self).get_context_data(**kwargs)
        object = self.object
        payment_orders = PaymentOrders.objects.filter(content_type=ContentType.objects.get_for_model(Order),
                                                      object_id__in=self.object_list.values('id')
                                                      )
        content.update(locals())
        return content


@method_decorator(staff_member_required, name='dispatch')
class CheckOrderPage(ListView):
    template_name = 'report/warehouse/check_orders.html'
    model = PaymentOrders
    paginate_by = 30

    def get_queryset(self):
        date_start, date_end = filter_date(self.request)
        queryset_o = PaymentOrders.objects.filter(is_check=True,
                                                  content_type=ContentType.objects.get_for_model(Order),
                                                  date_expired__range=[date_start, date_end]
                                                  )
        queryset_1 = PaymentOrders.objects.filter(is_check=True,
                                                  content_type=ContentType.objects.get_for_model(Vendor),
                                                  date_expired__range=[date_start, date_end]
                                                  )
        vendor_name = self.request.GET.getlist('vendor_name', None)
        if vendor_name:
            order_content = ContentType.objects.get_for_model(Order)
            orders_ids = Order.objects.filter(vendor__id__in=vendor_name).values_list('id')
            queryset_1 = queryset_1.filter(object_id__in=vendor_name)
            queryset_o = queryset_o.filter(content_type=order_content,
                                           object_id__in=orders_ids)
        queryset = queryset_o | queryset_1
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CheckOrderPage, self).get_context_data(**kwargs)
        vendors, payment_method, tt = initial_data_invoices()
        vendor_name = self.request.GET.getlist('vendor_name', None)
        not_paid_checks = self.object_list.filter(is_paid=False)
        not_paid_chart_analysis = not_paid_checks.values('payment_method__title').\
            annotate(total_value=Sum('final_value')).order_by('payment_method__title')
        context.update(locals())
        return context


@staff_member_required
def vendor_detail(request, pk):
    instance = get_object_or_404(Vendor, id=pk)
    # filters_data
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    vendors, categories, categories_site, colors, sizes, brands = initial_data_from_database()
    date_pick = request.GET.get('date_pick', None)

    # data
    products = Product.my_query.active().filter(vendor=instance)[:20]
    warehouse_orders = Order.objects.filter(vendor=instance, date_expired__range=[date_start, date_end])[:20]
    
    paychecks = list(chain(instance.payment_orders.all().filter(date_expired__range=[date_start, date_end]),
                           PaymentOrders.objects.filter(content_type=ContentType.objects.get_for_model(Order),
                                                        object_id__in=warehouse_orders.values('id'),
                                                        ) 
                          )
                    )[:20]
    order_item_sells = RetailOrderItem.objects.filter(title__in=products, order__date_expired__range=[date_start, date_end])[:20]
    context = locals()
    return render(request, 'report/details/vendors_id.html', context)


@method_decorator(staff_member_required, name='dispatch')
class OrderItemFlowView(ListView):
    template_name = 'report/warehouse_order_items_movements.html'
    model = OrderItem
    paginate_by = 100
    
    def get_queryset(self):
        date_start, date_end = filter_date(self.request)
        queryset = OrderItem.objects.filter(order__date_expired__range=[date_start, date_end])
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(OrderItemFlowView, self).get_context_data(**kwargs)
        date_start, date_end = filter_date(self.request)
        vendors = Vendor.objects.filter(active=True)
        context.update(locals())
        return context



@staff_member_required
def warehouse_order_items_movements(request):
    vendors, categories, categories_site, colors, sizes,  = initial_data_from_database()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    warehouse_order_items = get_filters_warehouse_order_items(request, OrderItem.objects.filter(
        order__day_created__range=[date_start, date_end]))
    currency = CURRENCY
    order_items_qty = warehouse_order_items.aggregate(Sum('qty'))['qty__sum'] if warehouse_order_items else 0
    order_items_total_value = warehouse_order_items.aggregate(total=Sum(F('total_clean_value')*F('qty')))['total'] if warehouse_order_items else 0
    avg_total_price = order_items_total_value/order_items_qty if order_items_qty > 0 else 0

    paginator = Paginator(warehouse_order_items, 100)
    page = request.GET.get('page')
    try:
        warehouse_order_items = paginator.page(page)
    except PageNotAnInteger:
        warehouse_order_items = paginator.page(1)
    except EmptyPage:
        warehouse_order_items = paginator.page(paginator.num_pages)
    context = locals()
    return render(request, 'report/warehouse_order_items_movements.html', context)


@staff_member_required
def products_movements(request):
    currency, table = CURRENCY, ToolsTableOrder.objects.get(title='reports_table_product_order')
    date_start, date_end, date_string = reports_initial_date(request)
    check_date = date_pick_session(request)
    if check_date:
        date_start, date_end, date_string = check_date
    vendors, warehouse_cate, colors, sizes = [Supply.objects.all(), Category.objects.all(), Color.objects.all(), Size.objects.all()]
    try:
        products_, sellings, buyings, returns, product_movements, filters_name = warehouse_movements_filters(request, date_start, date_end)
        # category_name, vendor_name, color_name , size_name, query, date_pick
        products, vendors_stats, warehouse_cate_stats, color_stats, size_stats, data_per_point = product_movenent_analysis(products_,
            date_start, date_end, sellings, buyings, returns)
        data_per_point.reverse()
        paginator = Paginator(tuple(products.items()), 50)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        page_ = request.GET.get('page_')
        paginator_ = Paginator(product_movements, 30)
        try:
            product_movements = paginator_.page(page_)
        except PageNotAnInteger:
            product_movements = paginator_.page(1)
        except EmptyPage:
            product_movements = paginator_.page(paginator_.num_pages)
    except:
        products, product_movements, filters_name = None, None, None
    context = locals()
    return render(request, 'reports/products_flow.html', context)


@staff_member_required
def category_report(request):
    categories, category_site, categories_info, categories_site_info = Category.objects.all(), CategorySite.objects.all(), {}, {}
    # get initial date from now and three months before.
    date_start, date_end, date_string = reports_initial_date(request)
    initial_order_item_buy = OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
    initial_order_item_sell = RetailOrderItem.my_query.selling_order_items(date_start=date_start, date_end=date_end)
    initial_order_item_return = RetailOrderItem.my_query.return_order_items(date_start, date_end)
    #initial_order_item_sell = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end])
    for cat in categories:
        qs_buy = initial_order_item_buy.filter(product__category__id=cat.id)
        qs_sell = initial_order_item_sell.filter(title__category=cat)
        qs_return = initial_order_item_return.filter(title__category__id=cat.id)
        categories_info[cat] = [qs_buy.aggregate(Sum('qty'))['qty__sum'] if qs_buy.aggregate(Sum('qty')) else 0,
                                qs_buy.aggregate(total=Sum(F('qty')*F('price')))['total'] if qs_buy.aggregate(total=Sum(F('qty')*F('price')))['total'] else 0,
                                qs_sell.aggregate(Sum('qty'))['qty__sum'] if qs_sell.aggregate(Sum('qty')) else 0,
                                qs_sell.aggregate(total=Sum(F('qty')*F('price')))['total'] if qs_sell.aggregate(total=Sum(F('qty')*F('price')))['total'] else 0,
                                ]
    for cat in category_site:
        categories_site_info[cat] = [qs_buy.aggregate(Sum('qty'))['qty__sum'] if qs_buy.aggregate(Sum('qty')) else 0,
                                qs_buy.aggregate(total=Sum(F('qty') * F('price')))['total'] if
                                qs_buy.aggregate(total=Sum(F('qty') * F('price')))['total'] else 0,
                                qs_sell.aggregate(Sum('qty'))['qty__sum'] if qs_sell.aggregate(Sum('qty')) else 0,
                                qs_sell.aggregate(total=Sum(F('qty') * F('price')))['total'] if
                                qs_sell.aggregate(total=Sum(F('qty') * F('price')))['total'] else 0,
                                ]
    context = locals()
    return render(request, 'reports/category_report.html', context)



@staff_member_required
def add_to_pre_order(request,dk,pk):
    product = Product.objects.get(id=dk)
    try:
        order = PreOrder.objects.filter(status='a').last()
        if request.POST:
            form = PreOrderItemForm(request.POST,initial={'title':product,
                                                          'order':order,})
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/reports/vendors/%s'%(pk))
        else:
            form =PreOrderItemForm(initial={'title':product,
                                            'order':order,})
        context={
            'form':form,
            'title':'Προσθήκη στην Προπαραγγελία.',
            'return_page':'/reports/vendors/%s'%(pk),
        }
        context.update(csrf(request))
        return render(request, 'inventory/create_costumer_form.html', context)
    except:
        messages.warning(request,'Δημιουργήστε Προπαραγγελία πρώτα.')
        return HttpResponseRedirect('/reports/vendors/%s'%(pk))



@staff_member_required
def reports_order_reset_payments(request, dk):
    order = Order.objects.get(id=dk)
    pay_orders = order.payorders_set.all()
    for pay_order in pay_orders:
        pay_order.delete_pay()
        pay_order.delete()
    pay_orders_deposit = order.vendordepositorderpay_set.all()
    for pay_order in pay_orders_deposit:
        pay_order.delete_deposit()
        pay_order.delete()
    order.credit_balance = 0
    order.status = 'p'
    order.save()
    return redirect('order_edit_main', dk=dk)




















