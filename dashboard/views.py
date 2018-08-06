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
from inventory_manager.models import Vendor, Category, OrderItem
from point_of_sale.models import RetailOrderItem
from inventory_manager.forms import CategoryForm
from my_site.models import CategorySite, Brands


WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS


@method_decorator(staff_member_required, name='dispatch')
class DashBoard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashBoard, self).get_context_data(**kwargs)
        eshop_orders = RetailOrder.my_query.eshop_new_orders()[:10]
        sent_orders = RetailOrder.my_query.eshop_sent_orders()[:10]
        last_items = RetailOrderItem.objects.filter(order__in=eshop_orders)[:10] if eshop_orders else []
        revenues = RetailOrder.my_query.paid_orders().aggregate(Sum('final_price'))['final_price__sum'] if RetailOrder.my_query.paid_orders() else 0
        carts = Cart.my_query.active_carts()
        currency = CURRENCY
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductsList(ListView):
    template_name = 'dashboard/products_list.html'
    model = Product
    paginate_by = 50
    total_products = 0

    def get_queryset(self):
        queryset = Product.objects.all()
        queryset = Product.filters_data(self.request, queryset)
        self.total_products = queryset.count() if queryset else 0
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsList, self).get_context_data(**kwargs)
        categories, vendors, colors, brands, site_categories = Category.objects.all(), Vendor.objects.all(), \
                                                               Color.objects.all(), Brands.objects.all(), \
                                                               CategorySite.objects.all()
        # get filters data
        search_name = self.request.GET.get('search_name', None)
        cate_name = self.request.GET.getlist('cate_name', None)
        site_cate_name = self.request.GET.getlist('site_cate_name', None)
        brand_name = self.request.GET.getlist('brand_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        color_name = self.request.GET.getlist('color_name', None)
        feat_name = self.request.GET.get('feat_name', None)
        active_name = self.request.GET.get('active_name', None)
        total_products = self.total_products
        products, currency = True, CURRENCY
        page_title = 'Product list'
        context.update(locals())
        return context

    def post(self, *args, **kwargs):
        get_products = self.request.POST.getlist('choice_name', None)
        new_brand = get_object_or_404(Brands, id=self.request.POST.get('change_brand')) \
            if self.request.POST.get('change_brand') else None
        new_category = get_object_or_404(Category, id=self.request.POST.get('change_cate')) \
            if self.request.POST.get('change_cate') else None
        new_cate_site = get_object_or_404(CategorySite, id=self.request.POST.get('change_cate_site')) \
            if self.request.POST.get('change_cate_site') else None
        new_vendor = get_object_or_404(Vendor, id=self.request.POST.get('change_vendor')) \
            if self.request.POST.get('change_vendor') else None
        print(new_cate_site)
        if new_brand and get_products:
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                print(product_id, product)
                product.brand = new_brand
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_brand.title)
            return redirect('dashboard:products')
        if new_category and get_products:
            for product_id in get_products:
                print('new category')
                product = get_object_or_404(Product, id=product_id)
                product.category = new_category
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_category.title)
            return redirect('dashboard:products')
        if new_cate_site and get_products:
            print('wtf')
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                product.category_site.add(new_cate_site)
                product.save()
            messages.success(self.request, 'The category %s added in the products' % new_cate_site.title)

        if new_vendor:
            queryset = Product.objects.all()
            queryset = Product.filters_data(self.request, queryset)
            queryset.update(supply=new_vendor)
            messages.success(self.request, 'The Vendor Updated!')
        return render(self.request, self.template_name)


@staff_member_required
def product_detail(request, pk):
    instance = get_object_or_404(Product, id=pk)
    products, currency, page_title = True, CURRENCY, '%s' % instance.title
    images = instance.get_all_images()
    sizes = instance.product_sizes.all()
    chars = instance.characteristics.all()
    form = UpdateProductForm(request.POST or None, instance=instance)

    if 'save_' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The products %s is saves!')
            return HttpResponseRedirect(reverse('dashboard:products'))

    if 'update_' in request.POST:
        form.save()
        messages.success(request, 'The products %s is edited!')
        return HttpResponseRedirect(reverse('dashboard:product_detail', kwargs={'pk': pk}))
    context = locals()
    return render(request, 'dashboard/product_detail.html', context)


@method_decorator(staff_member_required, name='dispatch')
class ProductAddMultipleImages(View):
    template_name = 'dashboard/form_set.html'

    def get(self, request, dk):
        instance = get_object_or_404(Product, id=dk)
        photos = ProductPhotos.objects.filter(product=instance)
        form = ProductPhotoForm()
        return render(request, self.template_name, context=locals())

    def post(self, request, dk):
        data = {}
        instance = get_object_or_404(Product, id=dk)
        form = ProductPhotoUploadForm()
        if request.POST:
            form = ProductPhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                photo = ProductPhotos.objects.create(product=instance,
                                                     image=form.cleaned_data.get('image')
                                                     )
                data = {'is_valid': True,
                        'name': photo.product.title,
                        'url': photo.image.url
                        }
        data['html_data'] = render_to_string(request=request,
                                             template_name='dashboard/ajax_calls/images.html',
                                             context={'photos': ProductPhotos.objects.filter(product=instance) }
                                            )
        print(data)
        return JsonResponse(data)


@staff_member_required
def edit_product_image(request, pk, action):
    instance = get_object_or_404(ProductPhotos, id=pk)
    if action == 'primary':
        if instance.is_primary:
            instance.is_primary = False
        else:
            instance.is_primary = True
    if action == 'secondary':
        if instance.is_back:
            instance.is_back = False
        else:
            instance.is_back = True
    instance.save()
    if action == 'delete':
        instance.delete()
    return HttpResponseRedirect(reverse('dashboard:product_add_images', kwargs={'dk': instance.product.id}))
    

@staff_member_required
def delete_product_image(request, pk):
    instance = get_object_or_404(ProductPhotos, id=pk)
    instance.delete()
    messages.success(request, 'The image has deleted')
    return HttpResponseRedirect(reverse('dashboard:product_detail', kwargs={'pk': instance.product.id}))


@staff_member_required
def product_add_sizechart(request, pk):
    instance = get_object_or_404(Product, id=pk)
    sizes_attr = instance.product_sizes.all()
    sizes = Size.objects.filter(active=True)
    if request.POST:
        for ele in request.POST:
            if ele.startswith('size_'):
                id = ele.split('_')[1]
                size = SizeAttribute.objects.get(id=id)
                size.qty = request.POST.get(f'{ele}', 0)
                size.save()
    return render(request, 'dashboard/size_chart.html', context=locals())


@staff_member_required
def delete_product_size(request, pk):
    instance = get_object_or_404(SizeAttribute, id=pk)
    retail_order_items = RetailOrderItem.objects.filter(size=instance)
    warehouse_orders = OrderItem.objects.filter(size=instance)
    if retail_order_items.exists() or warehouse_orders.exists():
        print('here!@')
        messages.warning(request, 'You cant delete this')
    else:
        instance.delete()
        messages.success(request, 'You deleted this size')
    return HttpResponseRedirect(reverse('dashboard:product_add_sizes', kwargs={'pk': instance.product_related.id}))


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteManagerView(ListView):
    template_name = 'dashboard/category_site_manager.html'
    model = CategorySite

    def get_queryset(self):
        queryset = CategorySite.objects.filter(active=True)
        search_name =  self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = CategorySite.filter_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategorySiteManagerView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk']) 
        context.update(locals())
        return context
    


@method_decorator(staff_member_required, name='dispatch')
class RelatedProductsView(ListView):
    model = Product
    template_name = 'dashboard/product_related_similar.html'

    def get_queryset(self):
        queryset = Product.objects.all()
        search_name = self.request.GET.get('search_name', None)
        if search_name:
            queryset = queryset.filter(title__icontains=search_name)
        queryset = queryset[:20]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(RelatedProductsView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        related_products = instance.related_products.all()
        search_name = self.request.GET.get('search_name', None)
        title = f'Add Related Products to {instance.title}'
        table_title = 'Related Products'
        context.update(locals())
        return context


@staff_member_required
def ajax_add_related_item(request, pk, dk):
    data = {}
    instance = get_object_or_404(Product, id=pk)
    related_instance = get_object_or_404(Product, id=dk)
    instance.related_products.add(related_instance)
    related_products = instance.related_products.all()
    data['html_data'] = render_to_string(request=request, template_name='dashboard/ajax_calls/related.html', context=locals())
    return JsonResponse(data)


@staff_member_required
def ajax_delete_related_product(request, pk, dk):
    data = {}
    instance = get_object_or_404(Product, id=pk)
    related_instance = get_object_or_404(Product, id=dk)
    instance.related_products.remove(related_instance)
    related_products = instance.related_products.all()
    data['html_data'] = render_to_string(request=request, template_name='dashboard/ajax_calls/related.html', context=locals())
    return JsonResponse(data)
    

@staff_member_required
def create_new_sizechart(request, dk, pk):
    data = dict()
    instance = get_object_or_404(Product, id=dk)
    size = get_object_or_404(Size, id=pk)
    size_exists = SizeAttribute.objects.filter(title=size, product_related=instance)
    if size_exists:
        data['new_'] = False
        sizes_attr = SizeAttribute.objects.filter(product_related=instance)
    else:
        data['new'] = True
        new_size = SizeAttribute.objects.create(title=size,
                                                product_related=instance
                                                )
        sizes_attr = SizeAttribute.objects.filter(product_related=instance)
    data['html_data'] = render_to_string(request=request, template_name='dashboard/ajax_calls/sizeattr.html', context=locals())
    return JsonResponse(data)


@method_decorator(staff_member_required, name='dispatch')
class SimilarColorProductsView(ListView):
    model = Product
    template_name = 'dashboard/product_related_similar.html'
    # i use the same template for related products too so with the boolean colors i change the data-url on template

    def get_queryset(self):
        queryset = Product.objects.all()
        search_name = self.request.GET.get('search_name', None)
        if search_name:
            queryset = queryset.filter(title__icontains=search_name)
        queryset = queryset[:20]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SimilarColorProductsView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        related_products = instance.different_color.all()
        title = f'Add Similar color Products to {instance.title}'
        table_title = 'Similar Color'
        colors = True
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context


@staff_member_required
def ajax_differenent_color_product_add_or_remove(request, pk, dk, choose):
    # if choose = 1 add if choose = 2 remove!
    data = {}
    colors = True
    instance = get_object_or_404(Product, id=pk)
    different_color = get_object_or_404(Product, id=dk)
    if choose == 1:
        instance.different_color.add(different_color)
    else:
        instance.different_color.remove(different_color)
    related_products = instance.different_color.all()
    data['html_data'] = render_to_string(request=request, template_name='dashboard/ajax_calls/related.html', context=locals())
    return JsonResponse(data)


@staff_member_required
def create_copy_item(request, pk):
    object = get_object_or_404(Product, id=pk)
    object.id = None
    object.slug = None
    object.save()
    return redirect(object.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class ProductCreate(CreateView):
    template_name = 'dashboard/product_create.html'
    form_class = CreateProductForm
    new_object = None

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('dashboard:product_detail', kwargs={'pk': self.new_object.id})


@staff_member_required
def delete_product(request, dk):
    instance = get_object_or_404(Product, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:products'))

