from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import RetailOrder, RetailOrderItem
from products.models import Product, SizeAttribute


@method_decorator(staff_member_required, name='dispatch')
class HomepagePoSView(ListView):
    template_name = ''
    model = RetailOrder
    paginate_by = 100

    def get_queryset(self):
        queryset = RetailOrder.objects.all()
        # queryset = RetailOrder.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomepagePoSView, self).get_context_data(**kwargs)
        search_name, paid_name, costumer_name = (self.request.GET.get('search_name', None),
                                                 self.request.GET.getlist('paid_name', None),
                                                 self.request.GET.getlist('costumer_name', None)
                                                 )
        context.update(locals())
        return context


@staff_member_required
def create_new_order(request):
    pass
