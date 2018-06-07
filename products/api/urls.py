from django.urls import path
from django.conf.urls import  include
from rest_framework import routers
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.DefaultRouter()
#router.register(r'products', ProductListApi)
#router.register(r'hproducts', ProductApiHyperView)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/test/', view=test_get_products),

    path('v1/products/', ProductListApi.as_view(), name='api_product_list'),
    path('v1/product/detail/<int:pk>/', ProductDetailApi.as_view(), name='api_product_detail'),

    
]

