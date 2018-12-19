from .views import *
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models.functions import TruncMonth

from .tools import initial_date


def ajax_analyse_vendors(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    vendor_name = request.GET.getlist('vendor_name[]', None)
    current_orders = Order.objects.filter(day_created__range=[date_start, date_end])
    current_orders = current_orders.filter(vendor__id__in=vendor_name) if vendor_name else current_orders
    current_analysis = current_orders.values('vendor__title').annotate(total_sum=Sum('total_price'))

    last_year_start, last_year_end = date_start - relativedelta(year=1), date_end -relativedelta(year=1)
    last_year_orders = Order.objects.filter(day_created__range=[last_year_start, last_year_end])
    last_year_orders = last_year_orders.filter(vendor__id__in=vendor_name) if vendor_name else last_year_orders
    last_year_analysis = current_orders.values('vendor__title').annotate(total_sum=Sum('total_price'))

    context = locals()
    data['test'] = render_to_string(request=request, template_name='report/ajax/vendor_analysis.html', context=context)
    return JsonResponse(data)


def ajax_vendors_page_analysis(request):
    data = dict()
    queryset = Vendor.objects.all()
    vendor_name, balance_name, search_pro, queryset = vendors_filter(request, queryset)
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)

    if request.GET.get('choice') == 'month':
        orders = Order.objects.filter(date_created__range=[date_start, date_end], vendor__id__in=vendor_name)
        month_data = orders.annotate(month=TruncMonth('date_created')).values('month')\
            .annotate(total_cost=Sum('total_price'),
                      total_paid=Sum('paid_value'))
        data['content'] = render_to_string(request=request,
                                           template_name='report/ajax/warehouse/vendors_analysis.html',
                                           context={'month_data': month_data,
                                                    'currency': CURRENCY
                                                    }
                                           )
    return JsonResponse(data)


def ajax_warehouse_category_analysis(request):
    data = {}
    data_type = request.GET.get('data_type')
    date_start, date_end = initial_date(request)
    category_name = request.GET.getlist('category_name')
    vendor_name = request.GET.getlist('vendor_name')

    if data_type == 'warehouse':
        queryset = OrderItem.objects.filter(order__date_expired__range=[date_start, date_end])
        queryset = queryset.filters_data(request, queryset)
        queryset_analysis = ''

    return JsonResponse(data)


def ajax_warehouse_product_movement_vendor_analysis(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    warehouse_order_items = get_filters_warehouse_order_items(request, OrderItem.objects.filter(
        order__day_created__range=[date_start, date_end]))
    product_analysis = warehouse_order_items.values('product').annotate(
        total_sum=Sum('total_clean_value')).order_by('-total_sum')
    category_analysis = warehouse_order_items.values('product__vendor__title').annotate(total_sum=Sum('total_clean_value'))
    data['product_analysis'] = render_to_string(request=request, template_name='report/ajax/warehouse-product-flow-analysis.html', context={'product_analysis': product_analysis,})
    return JsonResponse(data)




@staff_member_required
def ajax_balance_sheet_warehouse_orders(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    warehouse_orders = Order.objects.filter(day_created__range=[date_start, date_end])
    vendor_analysis = warehouse_orders.values('vendor__title').annotate(total_cost=Sum('total_price'),
                                                                        total_paid=Sum('paid_value'),
                                                                        ).order_by('-total_cost')
    print(vendor_analysis)
    context = locals()
    data['vendor_analysis'] = render_to_string(request=request, template_name='report/ajax/balance_sheet_warehouse_orders.html', context=context)
    return JsonResponse(data)


@staff_member_required
def ajax_balance_sheet_payroll(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    payroll_orders = PayrollInvoice.objects.filter(date_expired__range=[date_start, date_end])
    get_type = request.GET.get('request_type', None)
    data_analysis = payroll_orders.values('person__title').annotate(total_cost=Sum('value')
                                                                        ).order_by('-total_cost')
    if get_type == 'occupation':
        data_analysis = payroll_orders.values('person__occupation__title').annotate(total_cost=Sum('value')
                                                                        ).order_by('-total_cost')
    context = locals()
    data['payroll_analysis'] = render_to_string(request=request, template_name='report/ajax/ajax_payroll_balance_sheet.html', context=context)
    return JsonResponse(data)


@staff_member_required
def ajax_vendor_detail_product_analysis(request):
    data = {}


@staff_member_required
def ajax_retail_orders_payment_analysis(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    queryset = RetailOrder.my_query.sells_orders(date_start, date_end)
    queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick = \
            retail_orders_filter(request, queryset)
    data_analysis = queryset.values('payment_method__title').annotate(total_data=Sum('final_price')).order_by('total_data')
    context = locals()
    data['payment_analysis'] = render_to_string(request=request,
                                                template_name='report/ajax/retail_analysis.html',
                                                context=context,
                                                )
    return JsonResponse(data)
                