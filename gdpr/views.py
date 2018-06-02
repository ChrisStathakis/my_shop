from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView

from .models import CookiesModel, PolicyModel
# Create your views here.


def throw_cookie(request):
    return_obj = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return_obj.set_cookie("kolos", 'accept')
    return return_obj
    request.session.set_test_cookie()
    return HttpResponseRedirect('/')


def remove_cookie(request):
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    response.delete_cookie('kolos')
    return response


class CookiesPolicy(TemplateView):
    template_name = 'gdpr/cookies_policy.html'

    def get_context_data(self, **kwargs):
        context = super(CookiesPolicy, self).get_context_data(**kwargs)
        qs_exists = CookiesModel.objects.filter(active=True)
        if qs_exists:
            cookie_data  = qs_exists.last()
        context.update(locals())
        return context


class PrivacyPolicy(TemplateView):
    template_name = 'gdpr/privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super(CookiesPolicy, self).get_context_data(**kwargs)
        qs_exists = PrivacyPolicy.objects.filter(active=True)
        if qs_exists:
            cookie_data = qs_exists.last()
        context.update(locals())
        return context