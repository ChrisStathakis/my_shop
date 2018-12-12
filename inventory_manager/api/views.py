from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from inventory_manager.models import Order, OrderItem
from .serializers import WarehouseOrderSerializer, WarehouseOrderItemListSerializer


class ApiWarehouseOrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = WarehouseOrderSerializer


class ApiWarehouseOrderDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = WarehouseOrderSerializer


class ApiWarehouseOrderItemListView(ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = WarehouseOrderItemListSerializer

class ApiWarehouseOrderItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
