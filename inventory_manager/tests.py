from django.test import TestCase
from products.tests import ProductBasicTest
from products.models import Product
from .models import Order, OrderItem, Vendor


class WarehouseOrderTest(ProductBasicTest):

    def setUp(self):
        new_vendor = Vendor.objects.create(title='New Vendor')
        Order.objects.create()