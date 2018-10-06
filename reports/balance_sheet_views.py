from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


from point_of_sale.models import RetailOrder
from inventory_manager.models import Order
from transcations.models import Bill, Payroll, GenericExpense

from .tools import filter_date

@staff_member_required
def balance_sheet(request):
    date_start, date_end = filter_date(request)
    retail_orders = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
    warehouse_orders = Order.my_query.filter_by_date(date_start, date_end)
    bills = Bill.objects.filter(date_expired__range=[date_start, date_end])
    payroll = Payroll.objects.filter(date_expired__range=[date_start, date_end])
    expenses = GenericExpense.objects.filter(date_expired__range=[date_start, date_end])
    context = locals()
    return render(request, 'report/balance-sheet.html', context=locals())
    


