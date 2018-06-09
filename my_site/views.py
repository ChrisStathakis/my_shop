from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import auth, messages
from django.db.models import Q, Sum
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import  ListView, DetailView, View, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from urllib.parse import urlencode

from .tools import initial_filter_data, grab_user_filter_data, queryset_ordering
from .mixins import custom_redirect, SearchMixin
from .models import FirstPage, Banner, Brands, CategorySite
from products.models import Product, Color, ProductPhotos
from point_of_sale.models import RetailOrder, RetailOrderItem
from my_site.models import Shipping
from site_settings.models import PaymentMethod
from site_settings.constants import CURRENCY, PAYMENT_METHOD
from carts.views import check_if_cart_id, cart_data, check_or_create_cart
from carts.models import CartItem, Coupons
from carts.forms import CartItemCreate, CartItemCreateWithAttrForm
from .forms import CheckoutForm
from accounts.models import CostumerAccount
from accounts.forms import CostumerAccountForm


# from .forms import PersonalInfoForm
# from carts.forms import CartItemForm, CartItemNoAttrForm, CartItemCreate, CartItemCreateWithAttrForm
# return custom_redirect('url-name', x, q = 'something')
# Should redirect to '/my_long_url/x/?q=something'


def initial_data(request):
    menu_categories = CategorySite.objects.filter(show_on_menu=True)
    cart, cart_items = cart_data(request)
    return menu_categories, cart, cart_items


class Homepage(SearchMixin, TemplateView):
    template_name = 'my_site/index.html'

    def get_context_data(self, **kwargs):
        context = super(Homepage, self).get_context_data(**kwargs)
        first_page = FirstPage.active_first_page()
        featured_products = Product.my_query.get_site_queryset().featured()
        banners = Banner.objects.filter(active=True)
        menu_categories, cart, cart_items = initial_data(self.request)
        context.update(locals())
        return context


class NewProductsPage(SearchMixin, ListView):
    template_name = 'my_site/product_list.html'
    model = Product
    paginate_by = 16

    def get_queryset(self):
        queryset = Product.my_query.active_for_site()
        queryset = Product.filters_data(self.request, queryset)
        queryset = queryset_ordering(self.request, queryset)
        queryset = queryset[:160]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(NewProductsPage, self).get_context_data(**kwargs)
        seo_title = 'New Products'
        brands, categories, colors = initial_filter_data(self.object_list)
        menu_categories, cart, cart_items = initial_data(self.request)
        brand_name, cate_name, color_name = grab_user_filter_data(self.request)
        context.update(locals())
        return context


class OffersPage(SearchMixin, ListView):
    model = Product
    template_name = 'my_site/product_list.html'
    paginate_by = 16

    def get_queryset(self):
        queryset = Product.my_query.active_for_site().filter(price_discount__gte=0)
        queryset = Product.filters_data(self.request, queryset)
        queryset = queryset_ordering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OffersPage, self).get_context_data(**kwargs)
        seo_title = 'Offers'
        menu_categories, cart, cart_items = initial_data(self.request)
        brands, categories, colors = initial_filter_data(self.object_list)
        brand_name, cate_name, color_name = grab_user_filter_data(self.request)
        if 'search_name' in self.request.GET:
            search_name = self.request.GET.get('search_name')
            return custom_redirect('search_page', search_name=search_name)
        context.update(locals())
        return context


class CategoryPageList(SearchMixin, ListView):
    template_name = 'my_site/product_list.html'
    model = Product
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        self.category = get_object_or_404(CategorySite, slug=self.kwargs['slug'])
        self.categories = self.category.get_childrens()
        result_list = self.categories | CategorySite.objects.filter(id=self.category.id)
        queryset = Product.my_query.get_site_queryset().category_queryset(cate=result_list)
        queryset = Product.filters_data(self.request, queryset)
        queryset = queryset_ordering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryPageList, self).get_context_data(**kwargs)
        seo_title = self.category.title
        menu_categories, cart, cart_items = initial_data(self.request)
        brands, categories, colors = initial_filter_data(self.object_list)
        brand_name, cate_name, color_name = grab_user_filter_data(self.request)
        context.update(locals())
        return context


class BrandsPage(SearchMixin, ListView):
    template_name = 'my_site/brands.html'
    model = Brands

    def get_queryset(self):
        queryset = Brands.objects.filter(active=True)
        search_name = self.request.GET.get('search_brand', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrandsPage, self).get_context_data(**kwargs)
        seo_title = 'Brands Page'
        menu_categories, cart, cart_items = initial_data(self.request)
        search_name = self.request.GET.get('search_brand', None)
        context.update(locals())
        return context


class BrandPage(SearchMixin, ListView):
    template_name = 'my_site/product_list.html'
    model = Product
    brand = None
    slug_field = 'slug'

    def get_queryset(self, *args, **kwargs):
        instance = get_object_or_404(Brands, slug=self.kwargs['slug'])
        queryset = Product.my_query.active_for_site().filter(brand=instance)
        queryset = Product.filters_data(self.request, queryset)
        queryset = queryset_ordering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrandPage, self).get_context_data(**kwargs)
        instance = get_object_or_404(Brands, slug=self.kwargs['slug'])
        menu_categories, cart, cart_items = initial_data(self.request)
        brands, categories, colors = initial_filter_data(self.object_list)
        brand_name, cate_name, color_name = grab_user_filter_data(self.request)
        seo_title = '%s' % instance.title
        context.update(locals())
        return context


def product_detail(request, slug):
    instance = get_object_or_404(Product, slug=slug)
    menu_categories, cart, cart_items = initial_data(request)
    images = ProductPhotos.objects.filter(product=instance)
    seo_title = '%s' % instance.title
    if instance.size:
        form = CartItemCreateWithAttrForm(instance_related=instance)
    else:
        form = CartItemCreate()

    if request.POST:
        if instance.size:
            form = CartItemCreateWithAttrForm(instance, request.POST)
            if form.is_valid():
                qty = form.cleaned_data.get('qty', 1)
                attribute = form.cleaned_data.get('attribute')
                order = check_or_create_cart(request)
                CartItem.create_cart_item(request, order=order, product=instance, qty=qty, size=attribute)
                
                return HttpResponseRedirect(reverse('product_page', kwargs={'slug': instance.slug}))
        else:
            form = CartItemCreate(request.POST)
            if form.is_valid():
                qty = form.cleaned_data.get('qty', 1)
                order = check_or_create_cart(request)
                CartItem.create_cart_item(request, order=order, product=instance, qty=qty)
                messages.success(request, 'The product %s added in your cart' % instance.title)
                return HttpResponseRedirect(reverse('product_page', kwargs={'slug': instance.slug}))

    context = locals()
    return render(request, 'my_site/product_page.html', context)


class SearchPage(ListView):
    model = Product
    template_name = 'my_site/product_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.my_query.active_for_site()
        queryset = queryset.filter(title__icontains=self.search_name) if self.search_name else queryset
        queryset = Product.filters_data(self.request, queryset)
        queryset = queryset_ordering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchPage, self).get_context_data(**kwargs)
        menu_categories, cart, cart_items = initial_data(self.request)
        brands, categories, colors = initial_filter_data(self.object_list)
        brand_name, cate_name, color_name = grab_user_filter_data(self.request)
        seo_title = '%s' % self.search_name
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context

    def get(self, *args, **kwargs):
        self.search_name = self.request.GET.get('search_name', None)
        return super(SearchPage, self).get(*args, **kwargs)


class CartPage(SearchMixin, TemplateView):
    template_name = 'my_site/cart_page.html'

    def get_context_data(self, **kwargs):
        context = super(CartPage, self).get_context_data(**kwargs)
        menu_categories, cart, cart_items = initial_data(self.request)
        context.update(locals())
        return context

    def post(self, *args, **kwargs):
        menu_categories, cart, cart_items = initial_data(self.request)
        if self.request.POST.get('coupon_name', None):
            code = self.request.POST.get('coupon_name', None)
            find_coupon = Coupons.objects.filter(code=code, active=True)
            if find_coupon.exists():
                coupon = find_coupon.first()
                cart.coupon.add(coupon)
                cart.save()
                messages.success(self.request, 'Coupon %s added in your cart!' % code)
            else:
                messages.warning(self.request, 'This code is not a valid coupon')
        if self.request.POST:
            data = self.request.POST
            for key, value in data.items():
                print(key, value)
                if value == '0':
                    continue
                else:
                    try:
                        get_item = CartItem.objects.get(id=key)
                        get_item.qty = int(value)
                        get_item.save()
                    except:
                        continue
            messages.success(self.request, 'The cart updated!')
        cart.refresh_from_db()
        context = locals()
        return render(self.request, self.template_name, context=context)


def checkout_page(request):
    # del request.session['cart_id']
    form = CheckoutForm(request.POST or None)
    user = request.user.is_authenticated
    if user:
        profile = CostumerAccount.objects.get(user=user)
        print(profile)
        form = CheckoutForm(initial={'email': profile.user.email,
                                     'first_name': profile.user.first_name,
                                     'last_name': profile.user.last_name,
                                     'address': profile.shipping_address_1,
                                     'city': profile.shipping_city,
                                     'zip_code': profile.shipping_zip_code,
                                     'cellphone': profile.cellphone,
                                     'phone': profile.phone,
                                         
                                    })
    menu_categories, cart, cart_items = initial_data(request)
    if 'login_button' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if cart:
                cart.user = user
                cart.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if request.POST:
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cart_items = CartItem.objects.filter(order_related=cart)
            new_order = RetailOrder.create_order_from_cart(form, cart, cart_items)
            messages.success(request, 'Your Order Have Completed!')
            del request.session['cart_id']
            return HttpResponseRedirect(reverse('order_detail', kwargs={'dk': new_order.id}))
    context = locals()
    return render(request, 'my_site/checkout.html', context)


def delete_coupon(request, dk):
    coupon = get_object_or_404(Coupons, id=dk)
    menu_categories, cart, cart_items = initial_data(request)
    cart.coupon.remove(coupon)
    cart.save()
    messages.success(request, 'The coupon %s have been removed from cart' % coupon.code)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def user_profile_page(request):
    user = request.user
    profile = get_object_or_404(CostumerAccount, user=user)
    orders_list = RetailOrder.objects.filter(costumer_account=profile)
    profile_form = CostumerAccountForm(request.POST or None, instance=profile)
    if profile_form.is_valid():
        profile_form.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    return render(request, 'my_site/profile_page.html', context)  


@method_decorator(login_required, name='dispatch')
class FastOrdering(ListView):
    template_name = 'my_site/fast_ordering.html'
    model = RetailOrderItem

    def get_queryset(self):
        queryset = RetailOrderItem.objects.filter(order__costumer_account__user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FastOrdering, self).get_context_data(**kwargs)
        products = self.object_list.values('id', 'size__title' ).annotate(Sum('qty')).order_by('-qty__sum')[:5]
        most_used = []
        for ele in products:
            print(ele['id'])
            
            most_used.append((RetailOrderItem.objects.get(id=ele['id']), ele['qty__sum']))
        print(most_used)
        context.update(locals())
        return context



def order_detail_page(request, dk):
    get_order = get_object_or_404(RetailOrder, id=dk)
    print(request.user, get_order.costumer_account)
    if request.user != get_order.costumer_account.user:
        return HttpResponseRedirect('/')
    context = locals()
    return render(request, 'my_site/order_detail.html', context)



from django.http import HttpResponse
from reportlab.pdfgen import canvas


@login_required
def user_download_page(request):
    user = request.user
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{user.username}.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    data = ''
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

