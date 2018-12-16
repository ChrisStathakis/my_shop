from django.test import TestCase
from products.models import Product
from .models import RetailOrder, RetailOrderItem, Cart, CartItem
from django.conf import settings
import random
from string import ascii_letters


def generate_cart_id():
    new_id = ''
    for i in range(50):
        new_id = new_id + random.choice(ascii_letters)
    return new_id

class BasicTest(TestCase):

    def setUp(self):
        settings.WAREHOUSE_ORDERS_TRANSCATIONS = True
        settings.RETAIL_TRANSCATIONS = True
        Product.objects.create(title='Coca Cola', qty=5, price=10, price_buy=5)
        Product.objects.create(title='Sprite', qty=1, price=4, price_buy=1)
        Product.objects.create(title='Fanta', qty=4, price=5, price_buy=1)
        Product.objects.create(title='Coca', qty=0, price=2, price_buy=1)
        Product.objects.create(title='Test', qty=2, price=3, price_buy=2)
        RetailOrder.objects.create(title='Retail1', order_type='r')
        RetailOrder.objects.create(title='back1', order_type='b')

    def test_products(self):
        coca_cola = Product.objects.get(title='Coca Cola')
        self.assertEqual(coca_cola.qty, 5)


class RetailTranscationTest(BasicTest):

    def test_retail_order(self):
        retail_order = RetailOrder.objects.get(title='Retail1')
        coca_cola = Product.objects.get(title='Coca Cola')
        new_item = RetailOrderItem.objects.create(title=coca_cola,
                                                  order=retail_order,
                                                  qty=1,
                                                  value=coca_cola.final_price,
                                                  cost=coca_cola.price_buy
                                                  )
        new_item.update_order()
        self.assertEqual(new_item.final_value, coca_cola.final_price)
        self.assertEqual(retail_order.final_value, 10.00)
        self.assertEqual(retail_order.order_items.count(), 1)

    def test_warouhouse_transcation(self):
        retail_order = RetailOrder.objects.get(title='Retail1')
        coca_cola = Product.objects.get(title='Test')
        with self.settings(RETAIL_TRANSCATIONS=True):
            new_item = RetailOrderItem.objects.create(title=coca_cola,
                                                      order=retail_order,
                                                      qty=1,
                                                      value=coca_cola.final_price,
                                                      cost=coca_cola.price_buy
                                                      )
            new_item.update_order()
            new_item.update_warehouse('ADD', 1)
        self.assertEqual(coca_cola.qty, 1.00)

    def test_return_order_warehouse(self):
        retail_order = RetailOrder.objects.get(title='back1')
        coca_cola = Product.objects.get(title='Coca Cola')
        with self.settings(RETAIL_TRANSCATIONS=True):
            new_item = RetailOrderItem.objects.create(title=coca_cola,
                                                      order=retail_order,
                                                      qty=1,
                                                      value=coca_cola.final_price,
                                                      cost=coca_cola.price_buy
                                                      )
            new_item.update_order()
            new_item.update_warehouse('REMOVE', 1)
        self.assertEqual(coca_cola.qty, 6.00)

    def test_return_order(self):
        retail_order = RetailOrder.objects.get(title='back1')
        coca_cola = Product.objects.get(title='Coca Cola')
        new_item = RetailOrderItem.objects.create(title=coca_cola,
                                                  order=retail_order,
                                                  qty=1,
                                                  value=coca_cola.final_price,
                                                  cost=coca_cola.price_buy
                                                  )
        new_item.update_order()
        self.assertEqual(new_item.final_value, coca_cola.final_price)
        self.assertEqual(retail_order.final_value, 10.00)
        self.assertEqual(retail_order.order_items.count(), 1)


class TestEshopOrder(TestCase):

    def setUp(self):
        self.product = Product.objects.create(title='hello', qty=10, price=10)
        self.cart = Cart.objects.create(id_session=generate_cart_id())

    def test_cart(self):
        cart_item = CartItem.objects.create(order_related=self.cart, product_related=self.product, qty=1)
        self.assertEqual(self.cart.final_value, 10.00)



