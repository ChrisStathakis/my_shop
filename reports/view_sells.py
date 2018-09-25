from django.views.generic import  ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db.models import F, Sum

from .tools import initial_date, estimate_date_start_end_and_months
from point_of_sale.models import RetailOrder, RetailOrderItem

CURRENCY = settings.CURRENCY


@method_decorator(staff_member_required, name='dispatch')
class HomepageSellView(ListView):
    template_name = 'report/sales/homepage.html'
    model = RetailOrder

    def get_queryset(self):
        date_start, date_end, date_range = initial_date(self.request)
        queryset = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
        queryset = RetailOrder.eshop_orders_filtering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        content = super(HomepageSellView, self).get_context_data(**kwargs)
        currency = CURRENCY
        sells = self.object_list.filter(order_type__in=['r', 'e'])
        returns = self.object_list.filter(order_type='b')
        removes = self.object_list.filter(order_type='wr')
        total_sells, paid_sells = [sells.aggregate(Sum('final_value'))['final_value__sum'] if sells else 0,
                                   sells.aggregate(Sum('paid_value'))['paid_value__sum'] if sells else 0
                                   ]
        total_returns, paid_returns = [returns.aggregate(Sum('final_value'))['final_value__sum'],
                                       returns.aggregate(Sum('paid_value'))['paid_value__sum']
                                   ] if returns.exists() else [0, 0]
        total, paid_total = total_sells - total_returns, paid_sells - paid_returns
        # chart data
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        content.update(locals())
        return content


@method_decorator(staff_member_required, name='dispatch')
class OrderRetailReportView(DetailView):
    template_name = ''
    model = RetailOrder

    def get_context_data(self, **kwargs):
        content = super(OrderRetailReportView, self).get_context_data(**kwargs)
        order_items = self.object.order_items.all()
        payment_items = self.object.payment_items()
        content.update(locals())
        return content


