from django.views.generic import  ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from point_of_sale.models import RetailOrder, RetailOrderItem


@method_decorator(staff_member_required, name='dispatch')
class HomepageSellView(ListView):
    template_name = 'report/sales/homepage.html'
    model = RetailOrder

    def get_queryset(self):
        queryset = RetailOrder.objects.all()
        queryset = RetailOrder.eshop_orders_filtering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        content = super(HomepageSellView, self).get_context_data(**kwargs)

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


