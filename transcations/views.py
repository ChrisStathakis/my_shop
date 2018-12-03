from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.contenttypes.models import ContentType

from .models import Person, Occupation, Bill, BillCategory, GenericExpenseCategory, GenericExpense, Payroll
from .forms import BillForm, PayrollForm, PersonForm, OccupationForm, BillCategoryForm, GenericExpenseForm,\
    GenericExpenseCategoryForm

from site_settings.forms import PaymentForm
from site_settings.models import PaymentOrders
from inventory_manager.models import Vendor
from dateutil.relativedelta import relativedelta


def filters_data(request):
    search_name = request.GET.get('search_name', None)
    paid_name = request.GET.getlist('paid_name', None)
    cate_name = request.GET.getlist('cate_name', None)
    date_start, date_end = request.GET.get('date_start', None), request.GET.get('date_end', None)
    return search_name, paid_name, cate_name, date_start, date_end


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
    search_name, paid_name, cate_name, date_start, date_end = filters_data(request)
    queryset = Bill.filters_data(request, queryset)
    form = BillForm(request.POST or None)
    if 'new_bill' in request.POST:
        if form.is_valid():
            new_object = form.save(commit=False)
            new_object.user_account = request.user
            new_object.save()
            return HttpResponseRedirect(reverse('billings:bill_list'))
    paginator = Paginator(queryset, 50)
    page = request.GET.get('page')
    queryset = paginator.get_page(page)
    context = locals()
    return render(request, 'transcations/page_list.html', context)


@staff_member_required
def payroll_list_view(request):
    page_title, button_title, data_url = 'Payroll', 'Create Person', reverse('billings:ajax_payroll_person_popup')
    search_name, paid_name, cate_name, date_start, date_end = filters_data(request)
    person_name = request.GET.get('person_name', None)
    queryset = Payroll.objects.all()
    persons, categories = Person.objects.all(), Occupation.objects.all()
    queryset = Payroll.filters_data(request, queryset)
    form = PayrollForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New payroll added')
        return HttpResponseRedirect(reverse('billings:payroll_list'))
    context = locals()
    return render(request, 'transcations/page_list.html', context)


@staff_member_required
def edit_page(request, mymodel, pk, slug):
    my_form, instance = None, None
    if mymodel == 'bill':
        instance = get_object_or_404(Bill, id=pk)
        page_title, button_title, data_url = 'Bill', 'Create Bill', reverse('billings:ajax_bill_cat_popup')
        my_form = BillForm
    if mymodel == 'payroll':
        instance = get_object_or_404(Payroll, id=pk)
        page_title, button_title, data_url = 'Payroll', 'Create Payroll', reverse('billings:ajax_payroll_person_popup')
        my_form = PayrollForm
    if mymodel == 'expense':
        instance = get_object_or_404(GenericExpense, id=pk)
        page_title, button_title, data_url = 'Expense', 'Create Expense', reverse('billings:ajax_generic_cate_popup')
        my_form = GenericExpenseForm
    if slug == 'delete':
        instance.destroy_payments()
        instance.delete()
        instance.update_category()
        return HttpResponseRedirect(instance.get_dashboard_list_url())
    if slug == 'paid':
        instance.is_paid = True
        instance.save()
        instance.update_category()
        return HttpResponseRedirect(instance.get_dashboard_list_url())
    if request.GET:
        month = request.GET.get('month', 0)
        replays = request.GET.get('replays', 0)
        print(month, replays, mymodel, pk)
        return HttpResponseRedirect(reverse('billings:add_multi',
                                    kwargs={'expense_type': str(mymodel),
                                            'pk': pk,
                                            'month': int(month),
                                            'replays': int(replays)
                                            })
                                    )
    form = my_form(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        instance.update_category()
        messages.success(request, f'New {mymodel} added')
        return HttpResponseRedirect(instance.get_dashboard_list_url())
    context = locals()
    return render(request, 'transcations/page_detail.html', context)


@staff_member_required
def expenses_list_view(request):
    page_title, button_title, data_url = 'General Expenses', 'Create Expense Category', \
                                         reverse('billings:ajax_generic_cate_popup')
    search_name, paid_name, cate_name, date_start, date_end = filters_data(request)
    queryset = GenericExpense.objects.all()
    categories = GenericExpenseCategory.objects.all()
    form = GenericExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New expense added')
        return HttpResponseRedirect(reverse('billings:expenses_list'))
    context = locals()
    return render(request, 'transcations/page_list.html', context)


@staff_member_required
def add_multi_bills(request, expense_type, pk, month, replays):
    instance = get_object_or_404(Bill, id=pk) if expense_type == 'bill' else get_object_or_404(Payroll, id=pk) \
        if expense_type == 'payroll' else get_object_or_404(GenericExpense, id=pk)
    if replays > 0 and isinstance(replays, int):
        for ele in range(replays):
            instance.pk = None
            instance.date_expired += relativedelta(months=month)
            instance.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# settings  ------------------------------------------ settings  ------------------------------------------------


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
    template_name = 'transcations/class_page_detail.html'
    success_url = reverse_lazy('billings:person_list')

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        page_title, button_title, data_url = f'{self.object.title}', 'Create Occupation', reverse('billings:ajax_occup_popup')
        context.update(locals())
        return context

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
        page_title, button_title = 'Occupation', 'Create Person'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The occupation added!')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class OccupationDetailView(DetailView, UpdateView):
    model = Occupation
    form_class = OccupationForm
    template_name = 'transcations/class_page_detail.html'
    success_url = reverse_lazy('billings:occup_list')

    def get_context_data(self, **kwargs):
        context = super(OccupationDetailView, self).get_context_data(**kwargs)
        page_title, button_title = f'{self.object.title}', False
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Person is edited')
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
        page_title = 'Bill'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BillCategoryDetailView(DetailView, UpdateView):
    model = BillCategory
    form_class = BillCategoryForm
    template_name = 'transcations/class_page_detail.html'
    success_url = reverse_lazy('billings:bill_cate_list')

    def get_context_data(self, **kwargs):
        context = super(BillCategoryDetailView, self).get_context_data(**kwargs)
        page_title = f'{self.object.title}'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Person is edited')
        return super().form_valid(form)


  
@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCategoryListView(ListView, FormView):
    model = GenericExpenseCategory
    template_name = 'transcations/class_page_list.html'
    form_class = GenericExpenseCategoryForm
    success_url = reverse_lazy('billings:expense_cate_list')

    def get_queryset(self):
        queryset = GenericExpenseCategory.objects.all()
        queryset = GenericExpenseCategory.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GenericExpenseCategoryListView, self).get_context_data(**kwargs)
        page_title = 'Generic Expense Category'
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New category added!')


@method_decorator(staff_member_required, name='dispatch')
class GenericExpenseCategoryDetailView(DetailView, UpdateView):
    model = GenericExpenseCategory
    form_class = GenericExpenseCategoryForm
    template_name = 'transcations/class_page_detail.html'
    success_url = reverse_lazy('billings:expense_cate_list')

    def get_context_data(self, **kwargs):
        context = super(GenericExpenseCategoryDetailView, self).get_context_data(**kwargs)
        page_title = f'{self.object.title}'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Person is edited')
        return super().form_valid(form)



@method_decorator(staff_member_required, name='dispatch')
class CheckOrderView(ListView):
    model = PaymentOrders
    template_name = 'transcations/class_page_list.html'
    paginate_by = 100

    def get_queryset(self):
        queryset = PaymentOrders.objects.filter(is_check=True, content_type=ContentType.objects.get_for_model(Vendor))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = 'Checks'
        vendors = Vendor.objects.filter(active=True)
        vendor_name, search_name = self.request.GET.getlist('vendor_name', None), self.request.GET.get('search_name', None)
        context.update(locals())
        return context

