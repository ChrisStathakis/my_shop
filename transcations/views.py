from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import *
from .forms import BillForm
from site_settings.forms import PaymentForm
from site_settings.models import PaymentOrders
from dateutil.relativedelta import relativedelta


@staff_member_required
def homepage(request):
    bills = Bill.objects.all()[:10]
    generic_expenses = GenericExpense.objects.all()[:10]
    payrolls = Payroll.objects.all()[:10]
    return render(request, 'transcations/index.html', context=locals())


@staff_member_required
def bills_list_view(request):
    categories = BillCategory.objects.all()
    queryset = Bill.objects.all()
    form = BillForm(request.POST or None)
    if 'new_bill' in request.POST:
        if form.is_valid():
            print('here', form)
            form.save()
            return HttpResponseRedirect(reverse('billings:bill_list'))
    context = locals()
    return render(request, 'transcations/bill_list.html', context)


@staff_member_required
def edit_bill(request, pk, slug):
    instance = get_object_or_404(Bill, id=pk)
    categories = BillCategory.objects.all()
    queryset = Bill.objects.all()
    if action == 'delete':
        payment_orders = instance.payment_orders.all()
        for payment_order in payment_orders:
            payment_order.delete()
        instance.delete()
        messages.warning(request, f'The bill {instance.title} is deleted')
        return HttpResponseRedirect(reverse('billings:bill_list'))
    if action == 'paid':
        instance.is_paid=True
        instance.save()
        messages.warning(request, f'The bill {instance.title} is deleted')
        return HttpResponseRedirect(reverse('billings:bill_list'))

    form = BillForm(instance=instance)
    if request.POST:
        form = BillForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.warning(request, f'The bill {instance.title} is deleted')
            return HttpResponseRedirect(reverse('billings:bill_list'))

    context = locals()
    return render(request, 'transcations/bill_list.html', context)



