from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import *
from .forms import BillForm, PayrollForm, PersonForm
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
    page_title, button_title, data_url = 'Bills', 'Create Category', reverse('billings:ajax_bill_cat_popup')
    categories = BillCategory.objects.all()
    queryset = Bill.objects.all()
    search_name = request.GET.get('search_name', None)
    category_name = request.GET.getlist('category_name', None)
    queryset = Bill.filters_data(request, queryset)
    form = BillForm(request.POST or None)
    if 'new_bill' in request.POST:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('billings:bill_list'))
    paginator = Paginator(queryset, 25) 
    page = request.GET.get('page')
    queryset = paginator.get_page(page)
    context = locals()
    return render(request, 'transcations/page_list.html', context)


@staff_member_required
def edit_bill(request, pk, slug):
    instance = get_object_or_404(Bill, id=pk)
    page_title, button_title, data_url = f'{instance}', 'Create Category', reverse('billings:ajax_bill_cat_popup')
    payment_orders = instance.payment_orders.all()
    if slug == 'delete':
        payment_orders = instance.payment_orders.all()
        for payment_order in payment_orders:
            payment_order.delete()
        instance.delete()
        messages.warning(request, f'The bill {instance.title} is deleted')
        return HttpResponseRedirect(reverse('billings:bill_list'))
    if slug == 'paid':
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
    return render(request, 'transcations/page_detail.html', context)


@staff_member_required
def edit_bills_actions(request, pk, slug):
    instance = get_object_or_404(PaymentOrders, id=pk) if slug == 'payment_delete' else get_object_or_404(Bill, id=pk)
    if slug == 'save_as':
        new_instance = instance
        new_instance = None
        new_instance.save()
        new_instance.refresh_from_db()
        return HttpResponseRedirect(reverse('billings:bill_detail', kwargs={'pk': new_instance.id}))
    if slug == 'delete':
        for payorder in instance.payment_orders.all():
            payorder.delete()
        instance.delete()
        messages.warning(request, 'The bill is deleted!')
        return HttpResponseRedirect(reverse('billings:bill_list'))
    if slug == 'payment_delete':
        get_order = instance.content_object
        print(get_order)
        instance.delete()
        get_order.update_paid_value()
        messages.warning(request, 'The payment invoice is deleted')
        return HttpResponseRedirect(reverse('billings:bill_detail', kwargs={'pk': get_order.id}))
    return HttpResponseRedirect(reverse('billings:bill_detail', kwargs={'pk': instance.id}))



@staff_member_required
def payroll_list_view(request):
    page_title, button_title, data_url= 'Bills', 'Create Person', reverse('billings:ajax_payroll_person_popup')
    queryset = Payroll.objects.all()
    persons = Person.objects.all()
    occupations = Occupation.objects.all()
    form = PayrollForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New payroll added')
        return HttpResponseRedirect(reverse('billings:payroll_list'))
    context = locals()
    return render(request, 'transcations/page_list.html', context)


@staff_member_required
def edit_payroll(request, pk):
    instance = get_object_or_404(Payroll, id=pk)
    queryset = Payroll.objects.all()
    persons = Person.objects.all()
    occupations = Occupation.objects.all()
    form = PayrollForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'New payroll added')
        return HttpResponseRedirect(reverse('billings:payroll_list'))
    context = locals()
    return render(request, 'transcations/payroll_list.html', context)


@method_decorator(staff_member_required, name='dispatch')
class PersonListView(ListView, FormView):
    model = Person
    template_name = 'transcations/setting_list.html'
    form_class = PersonForm
    success_url = reverse_lazy('')

    def get_queryset(self):
        queryset = Person.objects.all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)

