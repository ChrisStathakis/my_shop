from django.urls import path
from .views import (general_homepage,
                    ShippingListApiView, ShippingDetailApiView,
                    PaymentMethodListApiView, PaymentMethodDetailApiView)


urlpatterns = [
    path('', general_homepage, name='api_general_homepage'),
    path('shipping-list/', ShippingListApiView.as_view(), name='api_shipping_list'),
    path('shipping-detail/<int:pk>/', ShippingDetailApiView.as_view(), name='api_shipping_detail'),
    path('payment-method-list/', PaymentMethodListApiView.as_view(), name='api_payment_method_list'),
    path('payment-method-detail/<int:pk>/', PaymentMethodDetailApiView.as_view(), name='api_payment_method_detail')

]