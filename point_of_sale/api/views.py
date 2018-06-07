from rest_framework import generics
from rest_framework import permissions
from rest_framework import renderers
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework.decorators import action

from ..models import RetailOrder, RetailOrderItem
from .serializers import RetailOrderSerializer




class RetailOrderListApi(generics.ListCreateAPIView):
    queryset = RetailOrder.objects.all()
    serializer_class = RetailOrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class RetailRenderer(generics.GenericAPIView):
    queryset = RetailOrder.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        return Response(order.title)

class RetailOrderViewset(viewsets.ModelViewSet):
    queryset = RetailOrder.objects.all()
    serializer_class = RetailOrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def title(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.order_items)

    def perfom_create(self, serializer):
        serializer.save(self.request.user)


