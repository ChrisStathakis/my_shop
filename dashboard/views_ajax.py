from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse
import json

from products.forms_popup import *
from products.forms import BrandForm, CategoryForm, ColorForm, SizeForm
from products.models import Brands
from inventory_manager.models import Category
from inventory_manager.forms import VendorQuickForm
from frontend.models import CategorySite
from frontend.forms import CategorySiteForm


def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category");</script>' % (instance.pk, instance))
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
def createVendorPopup(request):
    form = VendorQuickForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_vendor");</script>' % (instance.pk, instance))
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
def createCategorySitePopup(request):
    form = CategorySiteForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category_site");</script>' % (instance.pk, instance))
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
def createColorPopup(request):
    form = ColorForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
             '<script>opener.closePopup(window, "%s", "%s", "#id_color");</script>' % (instance.pk, instance)
        )
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@staff_member_required
def ajax_category_site_add(request, pk, dk, choice):
    data = {}
    instance = get_object_or_404(Product, id=pk)
    category = get_object_or_404(CategorySite, id=dk)
    if choice == 'add':
        instance.category_site.add(category)
    if choice == 'remove':
        instance.category_site.remove(category)
    data['table'] = render_to_string(request=request,
                                     template_name='dashboard/ajax_calls/category_site_manager.html',
                                     context = {'instance': instance}
                                     )
    return JsonResponse(data)


@staff_member_required
def ajax_category_site_search(request, pk):
    data = {}
    instance = get_object_or_404(Product, id=pk)
    search_name = request.GET.get('search_name', None)
    queryset = CategorySite.objects.filter(active=True)
    object_list = CategorySite.filter_data(queryset, search_name, active_name='1')
    data['table'] = render_to_string(request=request,
                                     template_name='dashboard/ajax_calls/category_site_search.html',
                                     context = {'object_list': object_list,
                                                'instance': instance
                                                }
                                     )
    return JsonResponse(data)
