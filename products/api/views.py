from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404

from .serializers import ProductSerializer, HyperProductSerializer, MySerializer
from ..models import Product

import requests
from django.urls import reverse
from django.shortcuts import render


def test_get_products(request):
    url = reverse('api_product_list')
    search_name = request.GET.get('search_name', None)
    response = requests.get(f'http://127.0.0.1:8000{url}')
    if search_name:
        response = requests.get(f'http://127.0.0.1:8000{url}?search_name={search_name}')
    data = response.json()
    return render(request, 'test.html', context={'data': data})
    

class ProductListApi(generics.ListCreateAPIView):
    queryset = Product.my_query.active_for_site()
    serializer_class = ProductSerializer

    def get_queryset(self):
        print('qww')
        queryset = Product.my_query.active_for_site()
        search_name = self.request.GET.get('search_name')
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset

class ProductDetailApi(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.my_query.active_for_site()
    serializer_class = ProductSerializer


