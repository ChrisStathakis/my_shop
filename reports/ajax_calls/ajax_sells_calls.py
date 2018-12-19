
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models.functions import TruncMonth

from reports.tools import initial_date
from reports.views import *

CuRRENCY = ''


@staff_member_required
def ajax_sells_analysis(request):
    data = dict()
    sellers_ids = request.GET.getlist('sell_point_name', None)
    sellers = User.objects.filter(id__in=sellers_ids) if sellers_ids else User.objects.none()
    date_start, date_end = filter_date(request)
    queryset = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
    queryset = RetailOrder.eshop_orders_filtering(request, queryset)
    data_analysis = queryset.values('seller_account__username').annotate(total_value=Sum('final_value')).order_by('total_value')
    data['result'] = render_to_string(template_name='report/sales/ajax_sells_analysis.html', 
                                      request=request, 
                                      context={
                                          'queryset': data_analysis,
                                          'currency': CURRENCY
                                          }
                                      )
    return JsonResponse(data)