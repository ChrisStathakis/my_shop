from django.views.generic import ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, Sum

from .tools import initial_date, filter_date, estimate_date_start_end_and_months, balance_sheet_chart_analysis
from point_of_sale.models import RetailOrder, RetailOrderItem
from site_settings.constants import ORDER_TYPES, ORDER_STATUS
from site_settings.tools import dashboard_filters_name
from inventory_manager.models import Vendor

CURRENCY = settings.CURRENCY
User = get_user_model()


@method_decorator(staff_member_required, name='dispatch')
class HomepageSellView(ListView):
    template_name = 'report/sales/homepage.html'
    model = RetailOrder
    paginate_by = 50
    
    def get_queryset(self):
        date_start, date_end = filter_date(self.request)
        queryset = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
        queryset = RetailOrder.eshop_orders_filtering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        content = super(HomepageSellView, self).get_context_data(**kwargs)
        currency = CURRENCY
        # populate filters
        order_types, order_status = ORDER_TYPES, ORDER_STATUS
        sell_points = User.objects.filter(is_active=True, is_staff=True)

        sells = self.object_list.filter(order_type__in=['r', 'e'])
        returns = self.object_list.filter(order_type='b')
        total_sells, paid_sells = [sells.aggregate(Sum('final_value'))['final_value__sum'] if sells else 0,
                                   sells.aggregate(Sum('paid_value'))['paid_value__sum'] if sells else 0
                                   ]
        total_returns, paid_returns = [returns.aggregate(Sum('final_value'))['final_value__sum'],
                                       returns.aggregate(Sum('paid_value'))['paid_value__sum']
                                   ] if returns.exists() else [0, 0]
        total, paid_total = total_sells - total_returns, paid_sells - paid_returns
        # chart data
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        warehouse_analysis = balance_sheet_chart_analysis(date_start, date_end, sells, 'final_value')
        # filters data
        date_start, date_end, date_range = initial_date(self.request)
        date_pick = self.request.GET.get('date_pick', None)
        search_name = self.request.GET.get('search_name', None)
        is_paid_name = self.request.GET.get('is_paid_name', None)
        payment_name = self.request.GET.getlist('payment_name', None)
        order_type_name = self.request.GET.getlist('order_type_name', None)
        order_status_name = self.request.GET.getlist('order_status_name', None)
        sell_point_name = self.request.GET.getlist('sell_point_name', None)
        print('sellers', sell_point_name)
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


@method_decorator(staff_member_required, name='dispatch')
class SellerReportView(ListView):
    model = User
    template_name = ''
    queryset = User.objects.filter(is_active=True, is_staff=True)
    

@method_decorator(staff_member_required, name='dispatch')
class CostumerReportView(ListView):
    model = User
    template_name = ''

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True, is_staff=False)

        return queryset


@method_decorator(staff_member_required, name='dispatch')
class SaleOrderItemListView(ListView):
    method = RetailOrderItem
    template_name = ''
    paginate_by = 50

    def get_queryset(self):
        date_start, date_end = filter_date(self.request)
        queryset = RetailOrderItem.my_query.all_orders_by_date_filter(date_start, date_end)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # filters_data
        date_start, date_end, search_name = dashboard_filters_name(self.request)
        return context