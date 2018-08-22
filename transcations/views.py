from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import *
from .forms import BillForm, PayrollForm, PersonForm, OccupationForm, BillCategoryForm
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
    template_name = 'transcations/class_page_list.html'
    form_class = PersonForm
    success_url = reverse_lazy('billings:person_list')
    paginate_by = 50

    def get_queryset(self):
        queryset = Person.objects.all()
        queryset = Person.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)
        page_title, button_title, data_url = 'Person', 'Create Occupation', reverse('billings:ajax_occup_popup')
        search_name = self.request.GET.get('search_name', None)
        occup_name = self.request.GET.getlist('occup_name', None)
        occupation = Occupation.objects.all()
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New Person Added')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PersonDetailView(DetailView, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = 'trans'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Person is edited')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OccupationListView(ListView, FormView):
    model = Occupation
    template_name = 'transcations/class_page_list.html'
    form_class = OccupationForm
    success_url = reverse_lazy('billings:occup_list')
    paginate_by = 50

    def get_queryset(self):
        queryset = Occupation.objects.all()
        queryset = Occupation.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OccupationListView, self).get_context_data(**kwargs)
        page_title, button_title = 'Ocuupation', 'Create Person'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The occupation added!')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryListView(ListView, FormView):
    model = BillCategory
    template_name = 'transcations/class_page_list.html'
    form_class = BillCategoryForm
    success_url = reverse_lazy('billing:bill_cate_list')

    def get_queryset(self):
        queryset = BillCategory.objects.all()
        queryset = BillCategory.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillCategoryListView, self).get_context_data(**kwargs)
        page_title, button_title = 'Bill', 'Create Person'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context

