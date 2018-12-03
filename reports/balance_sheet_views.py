from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from point_of_sale.models import RetailOrder
from inventory_manager.models import Order
from transcations.models import Bill, Payroll, GenericExpense
from site_settings.constants import CURRENCY

from .tools import filter_date
from itertools import chain
from site_settings.models import PaymentOrders
from operator import attrgetter

from django.db import connection, reset_queries



def create_month_analysis_from_database(queryset):
    data = queryset.annotate(month=TruncMonth('date_expired')
                                              ).values('month').annotate(final_value=Sum('final_value')
                                                                         ).order_by('month')
    return data

def estimate_months(querysets):
    months = []
    for queryset in querysets:
        for ele in queryset:
            if ele['month'] in months:
                continue
            else:
                months.append(ele['month'])
    return sorted(months)

def create_chart_data(months, queryset_per_month):
    results = []
    for month in months:
        month_str, total_value = month.strftime('%B'), 0
        for ele in queryset_per_month:
            if ele['month'] == month:
                total_value += ele['final_value']
        results.append([month_str, total_value])
    return results


@staff_member_required
def balance_sheet(request):
    date_start, date_end = filter_date(request)
    currency = CURRENCY
    retail_orders = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
    warehouse_orders = Order.my_query.filter_by_date(date_start, date_end)
    bills = Bill.objects.filter(date_expired__range=[date_start, date_end])
    payroll = Payroll.objects.filter(date_expired__range=[date_start, date_end])
    expenses = GenericExpense.objects.filter(date_expired__range=[date_start, date_end])


    # chart analysis
    invoices_per_month = create_month_analysis_from_database(warehouse_orders)
    bills_per_month  = create_month_analysis_from_database(bills)
    payroll_per_month = create_month_analysis_from_database(payroll)
    expenses_per_month = create_month_analysis_from_database(expenses)
    all_data_per_month  = list(chain(invoices_per_month, bills_per_month, payroll_per_month, expenses_per_month ))
    sells_per_month = create_month_analysis_from_database(retail_orders.filter(order_type__in=['e', 'r']))

    months = estimate_months([all_data_per_month, sells_per_month])
    months_str = list(month.strftime('%B') for month in months)
    chart_all_data = create_chart_data(months, all_data_per_month)
    chart_sell_data = create_chart_data(months, sells_per_month)
    chart_bills = create_chart_data(months, bills_per_month)
    chart_invoices = create_chart_data(months, invoices_per_month)
    chart_payroll = create_chart_data(months, payroll_per_month)
    chart_expenses = create_chart_data(months, expenses_per_month)

    # analyse incomes

    total_retail_value = retail_orders.filter(order_type='r').aggregate(Sum('final_value'))['final_value__sum'] if retail_orders.filter(order_type='r') else 0
    total_eshop_value = retail_orders.filter(order_type='e').aggregate(Sum('final_value'))['final_value__sum'] if retail_orders.filter(order_type='e') else 0
    total_sell_cost = retail_orders.filter(order_type__in=['r', 'e']).aggregate(Sum('total_cost'))['total_cost__sum'] if retail_orders.filter(order_type__in=['r', 'e']) else 0
    
    total_sell_value = total_eshop_value + total_retail_value
    diff = total_eshop_value - total_sell_cost
    # analyse outcomes

    total_invoice_value = warehouse_orders.aggregate(Sum('final_value'))['final_value__sum'] if warehouse_orders else 0
    total_bills_value = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills else 0
    total_payroll_value = payroll.aggregate(Sum('final_value'))['final_value__sum'] if payroll else 0
    total_expenses_value = expenses.aggregate(Sum('final_value'))['final_value__sum'] if expenses else 0

    total_cost_value = total_invoice_value + total_payroll_value + total_expenses_value + total_bills_value

    balance_sheet = total_sell_value - total_cost_value
    context = locals()
    return render(request, 'report/balance_sheet/balance-sheet.html', context=locals())
    

class CachFlowReportView(ListView):
    model = PaymentOrders
    template_name = 'report/balance_sheet/cash_report_view.html'

    def get_queryset(self):
        queryset = PaymentOrders.objects.filter(payment_method__id=1)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CachFlowReportView, self).get_context_data(**kwargs)
        expenses = self.object_list.filter(is_expense=True)
        incomes = self.object_list.filter(is_expense=False)
        context.update(locals())
        return context


