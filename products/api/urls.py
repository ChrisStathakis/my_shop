from django.urls import path
from django.conf.urls import  include
from rest_framework import routers
from .views import ProductApiView, ProductApiHyperView, product_list
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.DefaultRouter()
router.register(r'products', ProductApiView)
router.register(r'hproducts', ProductApiHyperView)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/test/', view=product_list),
]

