from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from point_of_sale.models import RetailOrder
from inventory_manager.models import Order
from transcations.models import Bill, Payroll, GenericExpense
from site_settings.constants import CURRENCY

from .tools import filter_date
from itertools import chain
from operator import attrgetter

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
    chart_invoices = warehouse_orders.annotate(month=TruncMonth('date_expired')
                                              ).values('month').annotate(final_value=Sum('final_value')
                                                                         ).order_by('month')
    chart_bills = bills.annotate(month=TruncMonth('date_expired')
                                                 ).values('month').annotate(final_value=Sum('final_value')
                                                                            ).order_by('month')
    chart_payroll = payroll.annotate(month=TruncMonth('date_expired')
                                                 ).values('month').annotate(final_value=Sum('final_value')
                                                                            ).order_by('month')
    chart_expenses = expenses.annotate(month=TruncMonth('date_expired')
                                                 ).values('month').annotate(final_value=Sum('final_value')
                                                                            ).order_by('month')

    chart_total_expenses = []
    months = []

    try_data = list(chain(chart_invoices, chart_expenses, chart_payroll, chart_bills))
    print(try_data)

    chart_sells = retail_orders.filter(order_type__in=['e', 'r']).annotate(month=TruncMonth('date_expired')
                                                 ).values('month').annotate(final_value=Sum('final_value')
                                                                            ).order_by('month')

    print(chart_sells, warehouse_orders)
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

    total_cost_value = total_invoice_value + total_payroll_value + total_expenses_value


    balance_sheet = total_sell_value - total_cost_value
    context = locals()
    return render(request, 'report/balance-sheet.html', context=locals())
    


