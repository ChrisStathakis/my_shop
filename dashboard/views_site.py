from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, View, FormView
from django.shortcuts import reverse, get_object_or_404, HttpResponseRedirect, get_list_or_404, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import F, Q
from django.contrib import  messages
from django.template.loader import render_to_string
from django.http import JsonResponse

from frontend.models import Banner
from carts.models import Coupons
from carts.forms import CouponForm, CouponQuickForm
from frontend.forms import BannerForm
from frontend.models import FirstPage, Banner
from frontend.forms import BannerForm, FirstPageForm
from accounts.models import User, CostumerAccount
from accounts.forms import CostumerAccountAdminForm, CreateUserAdmin, CostumerAccountDashboardForm
from products.models import Product, CategorySite, Brands, Gifts
from products.forms import GiftCreateForm, GiftEditForm
from .tools import product_filters_data, product_filters_get


from decimal import Decimal


@method_decorator(staff_member_required, name='dispatch')
class SiteView(TemplateView):
    template_name = 'dashboard/site_templates/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(SiteView, self).get_context_data(**kwargs)
        page_title = 'Site Settings'

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BannerView(ListView):
    model = Banner
    template_name = 'dashboard/site_templates/banners.html'

    def get_queryset(self):
        queryset = Banner.objects.all()
        active_name = self.request.GET.get('active_name', None)
        if active_name == '1':
            queryset = queryset.filter(active=True)
        if active_name == '2':
            queryset = queryset.filter(active=False)
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class BannerCreateView(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(BannerCreateView, self).get_context_data(**kwargs)
        page_title, back_url = 'Create Banner', self.get_success_url()
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:banner_view')


@method_decorator(staff_member_required, name='dispatch')
class BannerEditView(UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/form_view.html'

    def get_success_url(self):
        return reverse('dashboard:banner_view')


@staff_member_required
def banner_delete(request, pk):
    instance = get_object_or_404(Banner, id=pk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:banner_view'))


@method_decorator(staff_member_required, name='dispatch')
class CouponsView(ListView, FormView):
    model = Coupons
    template_name = 'dashboard/site_templates/coupons.html'
    form_class = CouponQuickForm

    def get_success_url(self):
        last_created = Coupons.objects.last()
        return reverse('dashboard:coupons_edit_view', kwargs={'pk': last_created.id})


    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New form added!')
        return super().form_valid(form)


@staff_member_required
def edit_coupon_view(request, pk):
    instance = get_object_or_404(Coupons, id=pk)
    categories = CategorySite.objects.all()
    form = CouponForm(instance=instance)
    if 'coupon_form' in request.POST:
        form = CouponForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:coupons_edit_view', kwargs={'pk', instance.id}))

    context = locals()
    return render(request, 'dashboard/site_templates/coupon_detail.html', context)


@staff_member_required
def ajax_edit_coupon_view(request, pk, dk, slug):
    data = {}
    instance = get_object_or_404(Coupons, id=pk)
    category = get_object_or_404(CategorySite, id=dk)
    if slug == 'add':
        instance.categories.add(category)
    if slug == 'delete':
        instance.categories.remove(category)
    data['table_data'] = render_to_string(request=request, 
                                          template_name='dashboard/ajax_calls/ajax_coupon.html', 
                                          context={'instance': instance}
                                          )
    return JsonResponse(data)


#  dashboard urls


@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    template_name = 'dashboard/site_templates/users_list.html'
    model = User
    paginate_by = 50

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False)
        search_name = self.request.GET.get('search_name', None)
        queryset = queryset.filter(username__icontains=search_name) if search_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class UserCreateView(CreateView):
    template_name = 'dashboard/form_view.html'
    model = User
    form_class = CreateUserAdmin
    success_url = reverse_lazy('dashboard:users_list')

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        page_title, back_url = 'Create New User', self.success_url
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@staff_member_required
def edit_user_view(request, pk):
    instance = get_object_or_404(User, id=pk)
    profile = CostumerAccount.objects.filter(user=instance).first()
    account_form = CreateUserAdmin(request.POST or None, instance=instance)
    profile_form = CostumerAccountDashboardForm(request.POST or None, instance=profile)
    if 'account' in request.POST:
        account_form.save()
        return HttpResponseRedirect(reverse('dashboard:edit_user', kwargs={'pk': pk}))
    if 'profile' in request.POST:
        profile_form.save()
        return HttpResponseRedirect(reverse('dashboard:edit_user', kwargs={'pk': pk}))
    context = locals()
    return render(request, 'dashboard/site_templates/edit_user.html', context)


@staff_member_required
def user_delete_view(request, pk):
    instance = get_object_or_404(User, id=pk)
    profiles = CostumerAccount.objects.filter(user=instance)
    for profile in profiles:
        profile.delete()
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:users_list'))


@staff_member_required
def delete_user(request, pk):
    pass


@method_decorator(staff_member_required, name='dispatch')
class CostumerListView(ListView):
    model = CostumerAccount
    template_name = 'dashboard/site_templates/costumer_list.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = CostumerAccount.objects.all()
        search_name = self.request.GET.get('search_name', None)
        queryset = queryset.filter(Q(name__icontains=search_name) |
                                   Q(user__username__icontains=search_name) |
                                   Q(user__last_name__icontains=search_name) |
                                   Q(user__first_name__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CostumerListView, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerAccountCreateView(CreateView):
    model = CostumerAccount
    form_class = CostumerAccountDashboardForm
    success_url = reverse_lazy('dashboard:costumers_list')
    template_name = 'dashboard/form_view.html'

    def form_valid(self, form):
        print('i ma here!')
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CostumerAccountCreateView, self).get_context_data(**kwargs)
        page_title, back_url = 'Create New Profile', self.success_url
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerAccountEditView(UpdateView):
    model = CostumerAccount
    form_class = CostumerAccountDashboardForm
    success_url = reverse_lazy('dashboard:costumers_list')
    template_name = 'dashboard/form_view.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CostumerAccountEditView, self).get_context_data(**kwargs)
        page_title, back_url, delete_url = 'Create New Profile', self.success_url, \
                                           reverse('dashboard:delete_profile', kwargs={'pk': self.kwargs['pk']})
        context.update(locals())
        return context


@staff_member_required
def delete_profile_view(request, pk):
    instance = get_object_or_404(CostumerAccount, id=pk)
    if instance.user:
        messages.warning(request, 'You need to delete the user first')
        return HttpResponseRedirect(reverse('dashboard:delete_profile', kwargs={'pk': pk}))
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:costumers_list'))


@staff_member_required
def discount_manager(request):
    queryset = Product.my_query.active()
    brands, categories, site_categories = product_filters_data()
    search_name, brand_name, category_name, category_site_name = product_filters_get(request)
    if request.POST:
        percent = request.POST.get('percent', None)
        price_ = request.POST.get('price', None)
        remove_discount = request.POST.get('remove_discount',None)
        if percent:
            modifier = Decimal((100-int(percent))/100)
            queryset.update(price_discount=F('price')*modifier)
        elif price_:
            queryset.update(price_discount=price_)
        elif remove_discount:
            queryset.update(price_discount=0)
    return render(request, 'dashboard/site_templates/discount_page.html', context=locals())


@method_decorator(staff_member_required, name='dispatch')
class PageConfigView(View):
    template_name = 'dashboard/page_config/index.html'

    def get(self, request):
        banners = Banner.objects.all()
        first_pages = FirstPage.objects.all()
        context = locals()
        return render(request, self.template_name, context)


@staff_member_required
def create_banner(request):
    form_title = 'Create Banner'
    form = BannerForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Banner added in gallery')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def edit_banner_page(request, dk):
    instance = get_object_or_404(Banner, id=dk)
    form_title = 'Edit %s' % instance.title
    form = BannerForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'The banner edited!')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def delete_banner(request, dk):
    banner = get_object_or_404(Banner, id=dk)
    banner.delete()
    return HttpResponseRedirect(reverse('dashboard:page_config'))


@staff_member_required
def create_first_page(request):
    form_title = 'Create Banner'
    form = FirstPageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Page added in gallery')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def edit_first_page(request, dk):
    instance = get_object_or_404(FirstPage, id=dk)
    form_title = 'Edit %s' % instance.title
    form = FirstPageForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'The banner edited!')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def delete_first_page(request, dk):
    get_object = get_object_or_404(FirstPage, id=dk)
    get_object.delete()
    return HttpResponseRedirect(reverse('dashboard:page_config'))


@staff_member_required
def gifts_view(request):
    object_list = Gifts.objects.all()
    form = GiftCreateForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        instance.refresh_from_db()
        return HttpResponseRedirect(reverse('dashboard:gift_detail', kwargs={'pk': instance.id}))
    context = locals()
    return render(request, 'dashboard/order_section/gifts.html', context)


@staff_member_required
def gifts_edit(request, pk):
    instance = get_object_or_404(Gifts, id=pk)
    related_products = instance.product_related.all()
    gift = instance.products_gift
    form = GiftCreateForm(instance=instance)
    if request.POST:
        form = GiftCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:gift_detail', kwargs={'pk': instance.id}))
    products = Product.my_query.get_site_queryset().active_for_site()
    context = locals()
    return render(request, 'dashboard/order_section/gifts_edit.html', context)


@staff_member_required
def gift_edit_products(request, pk, dk, type, sub):

    gift = get_object_or_404(Gifts, id=pk)
    instance = get_object_or_404(Product, id=dk)
    if type == 1:
        if sub == 1:
            gift.products_gift = instance
            gift.save()
        else:
            gift.products_gift = None
            gift.save()
    if type == 2:
        if sub == 1:
            gift.product_related.add(instance)
            gift.save()
        else:
            gift.product_related.remove(instance)
            gift.save()
    return HttpResponseRedirect(reverse('dashboard:gift_detail', kwargs={'pk': pk}))