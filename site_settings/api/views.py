from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from ..models import Shipping, PaymentMethod
from .serializers import (ShippingListSerializer, ShippingDetailSerializer,
                          PaymentMethodListSerializer, PaymentMethodDetailSerializer
                          )


@api_view(['GET'])
def general_homepage(request, format=None):
    return Response({
        'shipping': reverse('api_shipping_list', request=request, format=format),
        'payment_method': reverse('api_payment_method_list', request=request, format=format),

    })


class ShippingListApiView(generics.ListCreateAPIView):
    serializer_class = ShippingListSerializer
    queryset = Shipping.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class ShippingDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingDetailSerializer
    queryset = Shipping.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class PaymentMethodListApiView(generics.ListCreateAPIView):
    serializer_class = PaymentMethodListSerializer
    queryset = PaymentMethod.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class PaymentMethodDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodDetailSerializer
    queryset = PaymentMethod.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]