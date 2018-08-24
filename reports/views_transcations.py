from django.views.generic import ListView
from django.shortcuts import render
from transcations.models import *


def transcations_homepage(request):
    bills = BillCategory.my_query.get_queryset()
    payrolls = Person.my_query.get_queryset()
    expenses = GenericExpenseCategory.objects.filter(active=True)
    context = locals()
    return render(request, 'report/transcations/homepage.html', context)


class BillsReportView(ListView):
    model = Bill
    template_name = 'report/transcations/page_list.html'
    paginate_by = 100

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = Bill.objects.filter(date_expired__range=[date_start, date_end])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillsReportView, self).get_context_data(**kwargs)
        page__title, currency = 'Bils', CURRENCY
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        search_name, bill_name, paid_name = [self.request.GET.get('search_name'),
                                             self.request.GET.getlist('bill_name'),
                                             self.request.GET.get('paid_name')
                                            ]
        table_headers = ''
        my_values = self.object_list.values('date_expired', 'category', 'title', 'final_value', 'is_paid')
        context.update(locals())
        return context