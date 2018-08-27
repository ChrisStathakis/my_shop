from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from .forms import BillCategoryForm, PersonForm, OccupationForm, GenericExpenseCategoryForm
from .models import Bill, Payroll, GenericExpense, BillCategory, Person, GenericExpenseCategory


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
        return HttpResponse(f'<script>opener.closePopup(window, "{instance.pk}", "{instance}",'
                            f' "#id_person");</script>')
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})


def create_occup_popup(request):
    form = OccupationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(f"<script>opener.closePopup(window, '{instance.pk}', '{instance}', "
                            f"'#id_occupation');</script>")
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})


def create_generic_category_popup(request):
    form = GenericExpenseCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(f'<script>opener.closePopup(window, "{instance.pk}", "{instance.title}", '
                            f'"#id_genericexpensecategory");</script>')
    return render(request, '', context={'form': form})


def save_as_function(pk, model, slug):
    instance = get_object_or_404(model, id=pk)
    new_instance = instance
    new_instance.pk = None
    new_instance.is_paid = False
    new_instance.save()
    new_instance.refresh_from_db()



def fast_report(request, slug):
    data = {}
    queryset = BillCategory.objects.filter(balance__gt=0) if slug == 'bill' else Person.objects.all() \
        if slug == 'person' else GenericExpenseCategory.objects.all()
    data['results'] = render_to_string(request=request,
                                       template_name='gf.html',
                                       context={'slug': slug, "queryset": queryset}
                                       )
    return JsonResponse(data)


def save_as_view(request, pk, slug):
    if slug == 'bill':
        save_as_function(pk, Bill, slug)
        return HttpResponseRedirect(reverse('billings:edit_page',
                                            kwargs={'pk': Bill.objects.last().id,
                                                    'slug': 'edit',
                                                    'mymodel': slug})
                                    )
    elif slug == 'payroll':
        save_as_function(pk, Payroll, slug)
        print(Payroll.objects.last().id)
        return HttpResponseRedirect(reverse('billings:edit_page',
                                            kwargs={'pk': Payroll.objects.last().id,
                                                    'slug': 'edit',
                                                    'mymodel': slug})
                                    )
    elif slug == 'expenses':
        save_as_function(pk, GenericExpense, slug)
        return HttpResponseRedirect(reverse('billings:edit_page',
                                            kwargs={'pk': GenericExpense.objects.last().id,
                                                    'slug': 'edit',
                                                    'mymodel': slug})
                                    )
    else:
        return HttpResponseRedirect('/')

