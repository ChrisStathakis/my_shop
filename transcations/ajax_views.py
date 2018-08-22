from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .forms import BillCategoryForm, PersonForm, OccupationForm


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
    return render(request, 'dashboard/ajax_calls_popup_form.html', context={'form': form})