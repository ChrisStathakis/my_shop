from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .forms import BillCategoryForm, PersonForm, OccupationForm, GenericExpenseCategoryForm
from .models import Bill, Payroll, GenericExpense

def create_bill_category_popup(request):
    form = BillCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            f'<script>opener.closePopup(window, "{instance.pk}", "{instance}", "#id_category");</script>')
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})


def create_person_popup(request):
    form = PersonForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(f'<script>opener.closePopup(window, "{instance.pk}", "{instance}", "#id_person");</script>')
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})

def create_occup_popup(request):
    form = OccupationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(f"<script>opener.closePopup(window, '{instance.pk}', '{instance}', '#id_occupation');</script>")
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})

def create_generic_category_popup(request):
    form = GenericExpenseCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(f'<script>opener.closePopup(window, "{instance.pk}", "{instance.title}", "#id_genericexpensecategory");</script>')
    return render(request, '', context={'form': form})


def save_as_function(url, pk, model):
    instance = get_object_or_404(model, id=pk)
    new_instance = instance
    new_instance.pk = None
    new_instance.is_paid = False
    new_instance.save()
    new_instance.refresh_from_db()
    return HttpResponseRedirect(reverse(f'{url}', kwargs={'pk': new_instance.id, 'slug':'edit'}))

def save_as_view(request, pk, slug):
    print('save_As')
    if slug == 'bill':
        print('here')
        save_as_function('billings:edit_bill', pk, Bill)
    if slug == 'payroll':
        save_as_function('billings:edit_payroll', pk, Payroll)
    if slug == 'expenses':
        save_as_function('billings:edit_expense', pk, GenericExpense)
    return HttpResponseRedirect('/')