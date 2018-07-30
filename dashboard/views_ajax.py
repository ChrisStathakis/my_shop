from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
import json

from products.forms_popup import *
from products.forms import BrandForm, CategoryForm, ColorForm, SizeForm
from products.models import Brands
from inventory_manager.models import Category

def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))
    return render(request, "dashboard/ajax_calls/popup_form.html", {"form": form})


def category_edit(request, pk=None):
    instance = get_object_or_404(Category, id=pk)
    form = CategoryForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' %
                            (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@csrf_exempt
def get_category_id(request):
    if request.is_ajax():
        category_name = request.GET.get('cate_name')
        category_id = Category.objects.get(title=category_name).id
        data = {'category_id': category_id,}
        return JsonResponse(data)
    return HttpResponse("/")


def product_action(action_type):
    pass


@staff_member_required
def createBrandPopup(request):
    form = BrandForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_brand");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})



@staff_member_required
def createCategoryPopup(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@staff_member_required
def get_brand_id(request):
    if request.is_ajax():
        author_name = request.GET['author_name']
        author_id = Brands.objects.get(title=author_name).id
        data = {'author_id': author_id, }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")


@staff_member_required
def create_color_popup(request):
    form = ColorForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
             '<script>opener.closePopup(window, "%s", "%s", "#id_brand");</script>' % (instance.pk, instance)
        )
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})