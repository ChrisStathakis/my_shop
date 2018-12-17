from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework import permissions
from inventory_manager.models import Order, OrderItem
from .serializers import WarehouseOrderSerializer, WarehouseOrderItemListSerializer


@api_view(['GET'])
def api_warehouse_homepage(request, format=None):
    return Response({
        'order': reverse('api_inventory:warehouse_order_list', request=request, format=None)
    })


class ApiWarehouseOrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = WarehouseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class ApiWarehouseOrderDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = WarehouseOrderSerializer


class ApiWarehouseOrderItemListView(ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = WarehouseOrderItemListSerializer


class ApiWarehouseOrderItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
