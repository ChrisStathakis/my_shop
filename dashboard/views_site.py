from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import reverse, get_object_or_404, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from my_site.models import Banner
from carts.models import Coupons
from my_site.forms import BannerForm
from my_site.models import FirstPage, Banner
from my_site.forms import BannerForm, FirstPageForm
from accounts.models import User, CostumerAccount
from accounts.forms import CostumerAccountAdminForm, CreateUserAdmin


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
class CouponsView(ListView):
    model = Coupons
    template_name = 'dashboard/site_templates/coupons.html'


@method_decorator(staff_member_required, name='dispatch')
class CouponCreate(CreateView):
    model = Coupons
    form_class = ''
    template_name = ''
    success_url = reverse_lazy('dashboard:coupons_view')




#  dashboard urls

@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    template_name = 'accounts/dash_user_list.html'
    model = CostumerAccount
    paginate_by = 50

    
@method_decorator(staff_member_required, name='dispatch')
class UserUpdateView(UpdateView):
    template_name = 'dash_ware/form.html'
    model = CostumerAccount
    form_class = CostumerAccountAdminForm
    success_url = reverse_lazy('accounts:dash_list')

    def get_initial(self):
        initial = super(UserUpdateView,self).get_initial()
        initial['email'] = self.object.user.email
        print(self.object.user.email)
        return initial

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        page_title = f'{self.object}'
        back_url = self.success_url
        context.update(locals())
        return context




@method_decorator(staff_member_required, name='dispatch')
class UserCreateView(CreateView):
    template_name = 'dash_ware/form.html'
    model = User
    form_class = CreateUserAdmin
 

    def get_success_url(self):
        get_last_object = User.objects.last()
        return reverse('accounts:dash_update', kwargs={'pk': get_last_object.id})


@staff_member_required
def delete_user(request, pk):
    pass


@method_decorator(staff_member_required, name='dispatch')
class UsersPage(ListView):
    model = CostumerAccount
    template_name = 'dashboard/user_section/index.html'

    def get_context_data(self, **kwargs):
        context = super(UsersPage, self).get_context_data(**kwargs)

        return context


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