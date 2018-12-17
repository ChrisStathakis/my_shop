from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response


@api_view(['GET'])
def homepage(request, format=None):
    return Response({
        'transcations': reverse('api_homepage_transcation', request=request, format=format),
        'general': reverse('api_general_homepage', request=request, format=format),
        'inventory_manager': reverse('api_inventory:api_warehouse_homepage', request=request, format=format)
    })
