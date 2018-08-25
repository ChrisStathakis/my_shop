from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from transcations.models import *


def transcations_homepage(request):
    bills = BillCategory.my_query.get_queryset().is_active()
    payrolls = Person.my_query.get_queryset().is_active()
    expenses = GenericExpenseCategory.objects.filter(active=True)
    context = locals()
    return render(request, 'report/transcations/homepage.html', context)


@method_decorator(staff_member_required, name='dispatch')
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
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PayrollReportView(ListView):
    model = Payroll
    template_name = ''
    paginate_by = 50

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = Payroll.objects.filter(date_expired__range=[date_start, date_end])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PayrollReportView, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        search_name, bill_name, paid_name = [self.request.GET.get('search_name'),
                                             self.request.GET.getlist('bill_name'),
                                             self.request.GET.get('paid_name')
                                            ]
        persons = Person.my_query.get_queryset().is_active()
        Occupations = Occupation.my_query.get_queryset().is_active()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GenericExpense(ListView):
    model = GenericExpense
    template_name = ''
    paginate_by = 100

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = self.model.objects.filter(date_expired__range=[date_start, date_end])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GenericExpense, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        search_name, bill_name, paid_name = [self.request.GET.get('search_name'),
                                             self.request.GET.getlist('bill_name'),
                                             self.request.GET.get('paid_name')
                                            ]
        context.update(locals())


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryDetail(ListView):
    model = Bill
    template_name = ''
    paginate_by = 50

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        instance = get_object_or_404(BillCategory, kwargs={id: self.kwargs['pk']})
        queryset = self.model.objects.filter(category=instance, date_expired__range=[date_start, date_end])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillCategory, self).get_context_data(**kwargs)

        return context