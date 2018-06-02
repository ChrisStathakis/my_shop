from django.urls import path
from .views import throw_cookie, remove_cookie, CookiesPolicy, PrivacyPolicy

urlpatterns = [
    path('throw', view=throw_cookie, name='throw_cookie'),
    path('remove', view=remove_cookie, name='remove_cookie'),
    path('cookies-policy', CookiesPolicy.as_view(), name='cookies_policy'),
    path('privacy-policy', CookiesPolicy.as_view(), name='privacy_policy'),

]
