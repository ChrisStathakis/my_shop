from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import *
from .forms import BillForm
from site_settings.forms import PaymentForm
from dateutil.relativedelta import relativedelta


@staff_member_required
def homepage(request):
    bills = Bill.objects.all()[:10]
    generic_expenses = GenericExpense.objects.all()[:10]
    payrolls = Payroll.objects.all()[:10]
    return render(request, 'transcations/index.html', context=locals())


@method_decorator(staff_member_required, name='dispatch')
class BillListView(ListView, FormView):
    model = Bill
    template_name = 'transcations/bill_list.html'
    paginate_by = 20
    form_class = BillForm

    

    def get_context_data(self, **kwargs):
        context = super(BillListView, self).get_context_data(**kwargs)
        categories = BillCategory.objects.all()
        
        context.update(locals())