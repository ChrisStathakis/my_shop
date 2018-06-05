from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .serializers import ProductSerializer, HyperProductSerializer, MySerializer
from ..models import Product


class ProductApiView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductApiHyperView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = HyperProductSerializer


@csrf_exempt
def product_list(request):
    if request.method == "GET":
        print('get')
        products = Product.objects.all()
        serializer = MySerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.POST:
        print('get')
        data = JSONParser().parse(request)
        serializer = MySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)