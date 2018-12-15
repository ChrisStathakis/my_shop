from django.test import TestCase
from products.models import Product
from .models import Order, OrderItem, Vendor


class WarehouseOrderTest(TestCase):

    def setUp(self):
        new_vendor = Vendor.objects.create(title='New Vendor')
        Order.objects.create(title='test_1', vendor=new_vendor, order_type='1')
        Product.objects.create(title='Coca Cola', qty=0, vendor=new_vendor)

    def test_order(self):
        order = Order.objects.get(title='test_1')
        vendor = Vendor.objects.first()
        self.assertEqual(order.vendor, vendor)

    def test_warehouse_qty(self):
        order = Order.objects.get(title='test_1')
        product = Product.objects.get(title='Coca Cola')
        new_item = OrderItem.objects.create(product=product,
                                            order=order,
                                            qty=5,
                                            )
        with self.settings(WAREHOUSE_ORDERS_TRANSCATIONS=True):
            new_item.quick_add_to_order(5)
        self.assertEqual(product.qty, 5.00)

