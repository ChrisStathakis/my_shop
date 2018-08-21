from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .forms import BillCategoryForm


def create_bill_category_popup(request):
    print('here')
    form = BillCategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            f'<script>opener.closePopup(window, "{instance.pk}", "{instance}", "#id_category");</script>')
    return render(request, 'dashboard/ajax_calls/popup_form.html', context={'form': form})