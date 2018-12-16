from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, FormView, View
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.forms import formset_factory, inlineformset_factory
from django.conf import settings
from dateutil.relativedelta import relativedelta

from point_of_sale.models import RetailOrder, RetailOrderItem
from carts.models import Cart, CartItem
from products.models import Product, Color, ProductCharacteristics, SizeAttribute, ProductPhotos, Size
from products.forms import (SizeAttributeForm, UpdateProductForm, ProductPhotoForm,
                            CreateProductForm, CategorySiteForm, BrandForm, SizeForm, ColorForm
                            )

from carts.models import Cart
from products.forms_popup import ProductPhotoUploadForm
from site_settings.constants import CURRENCY
from inventory_manager.models import Vendor, Category
from inventory_manager.forms import CategoryForm
from frontend.models import CategorySite, Brands


@method_decorator(staff_member_required, name='dispatch')
class CategoryPage(ListView):
    template_name = 'dashboard/page_list.html'
    model = Category
    paginate_by = 50

    def get_queryset(self):
        queryset = Category.objects.all()
        active_name, show_name, search_name = [self.request.GET.getlist('active_name'),
                                               self.request.GET.getlist('show_name'),
                                               self.request.GET.get('search_name')
                                               ]
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name == ['1'] else queryset.filter(active=False) \
            if active_name == ['2'] else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)
        title, create_title, create_url, category_page = 'Categories', 'Create Category', reverse('dashboard:category_create', kwargs={}), True
        active_name, show_name, search_name = [self.request.GET.getlist('active_name'),
                                               self.request.GET.getlist('show_name'),
                                               self.request.GET.get('search_name')
                                               ]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryDetail(UpdateView):
    template_name = 'dashboard/page_detail.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard:categories')

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryCreate(CreateView):
    template_name = 'dashboard/page_create.html'
    form_class = CategoryForm

    def get_context_data(self, **kwargs):
        context = super(CategoryCreate, self).get_context_data(**kwargs)
        title = 'Create Category'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:categories')


@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    category.delete()
    messages.warning(request, 'The category has deleted')
    return redirect(reverse('dashboard:categories'))


# -- CATEGORY SITE

@method_decorator(staff_member_required, name='dispatch')
class CategorySitePage(ListView):
    template_name = 'dashboard/category_site_list.html'
    model = CategorySite
    paginate_by = 50

    def get_queryset(self):
        queryset = CategorySite.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = CategorySite.filter_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategorySitePage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        page_title = 'Site Categories'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteEdit(UpdateView):
    model = CategorySite
    form_class = CategorySiteForm
    template_name = 'dashboard/page_create.html'

    def get_context_data(self, **kwargs):
        context = super(CategorySiteEdit, self).get_context_data(**kwargs)
        title = f'{self.object}'
        delete_url = reverse('dashboard:delete_category_site', kwargs={'pk': self.kwargs.get('pk')})
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The category edited successfuly!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:categories_site')


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteCreate(CreateView):
    model = CategorySite
    template_name = 'dashboard/page_create.html'
    form_class = CategorySiteForm

    def get_context_data(self, **kwargs):
        context = super(CategorySiteCreate, self).get_context_data(**kwargs)
        title = 'Create New Site Category'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:categories_site')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New category added!')
        return super().form_valid(form)


@staff_member_required
def delete_category_site(request, pk):
    instance = get_object_or_404(CategorySite, id=pk)
    instance.delete()
    messages.warning(request, f'The category {instance.title} is deleted')
    return HttpResponseRedirect(reverse('dashboard:categories_site'))

#  -- BRANDS


@method_decorator(staff_member_required, name='dispatch')
class BrandPage(ListView):
    template_name = 'dashboard/brand_list.html'
    model = Brands
    paginate_by = 50

    def get_queryset(self):
        queryset = Brands.objects.all()
        search_name = self.request.GET.get('search_name', None)
        queryset = Brands.filters_data(queryset, self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrandPage, self).get_context_data(**kwargs)
        title, create_title, create_url = 'Brands', 'Create Brand', ''
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        context.update(locals())
        return context


@staff_member_required
def brandEditPage(request, pk):
    instance = get_object_or_404(Brands, id=pk)
    form_title = instance.title
    delete_url = reverse('dashboard:delete_brand', kwargs={'pk': pk})
    form = BrandForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:brands'))
    context = locals()
    return render(request, 'dashboard/form_view.html', context)


@method_decorator(staff_member_required, name='dispatch')
class BrandsCreate(CreateView):
    form_class = BrandForm
    template_name = 'dashboard/page_create.html'

    def get_context_data(self, **kwargs):
        context = super(BrandsCreate, self).get_context_data(**kwargs)
        title = 'Create Brand'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Brand Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:brands')


@staff_member_required
def delete_brand(request, pk):
    instance = get_object_or_404(Brands, id=pk)
    instance.delete()
    messages.warning(request, 'The brand %s has deleted' % instance.title)
    return redirect(reverse('dashboard:brands'))


# -- COLOR

@method_decorator(staff_member_required, name='dispatch')
class ColorPage(ListView):
    template_name = 'dashboard/color_list.html'
    model = Color
    paginate_by = 50

    def get_queryset(self):
        queryset = Color.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = Color.filters_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ColorPage, self).get_context_data(**kwargs)
        page_title, create_title, create_url = 'Colors', 'Create Color', reverse('dashboard:color_create')
        table_thead = ['id', 'Name', 'Active']
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ColorEditPage(UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(ColorEditPage, self).get_context_data(**kwargs)
        page_title, back_url = 'Edit Color', reverse('dashboard:colors')
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Th color edited!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:colors')


@method_decorator(staff_member_required, name='dispatch')
class ColorCreate(CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'dashboard/page_create.html'

    def get_context_data(self, **kwargs):
        context = super(ColorCreate, self).get_context_data(**kwargs)
        title = 'Create Color'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The color Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:colors')


@staff_member_required
def delete_color(request, pk):
    instance = get_object_or_404(Color, id=pk)
    instance.delete()
    messages.warning(request, 'The color %s deleted' % instance.title)
    return redirect(reverse('dashboard:colors'))


# -- SIZE

@method_decorator(staff_member_required, name='dispatch')
class SizePage(ListView):
    template_name = 'dashboard/size_list.html'
    model = Size
    paginate_by = 50

    def get_queryset(self):
        queryset = Size.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = Size.filters_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SizePage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        page_title = 'Sizes'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class SizeEditPageView(UpdateView):
    form_class = SizeForm
    template_name = 'dashboard/form_view.html'
    model = Size
    success_url = reverse_lazy('dashboard:sizes')

    def get_context_data(self, **kwargs):
        context = super(SizeEditPageView, self).get_context_data(**kwargs)
        page_title = form_title = 'Edit Size'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The size had edited')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class SizeCreate(CreateView):
    model = Size
    form_class = SizeForm
    template_name = 'dashboard/form_view.html'

    def get_initial(self):
        initial = {}
        initial['user_account'] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super(SizeCreate, self).get_context_data(**kwargs)
        page_title = form_title = 'Create Size'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Brand Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:sizes')

















