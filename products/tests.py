from django.test import TestCase
from .models import Product


class ProductBasicTest(TestCase):

    def setUp(self):
        Product.objects.create(title='Coca Cola', qty=5, price=10, price_buy=5)
        Product.objects.create(title='Sprite', qty=1, price=4, price_buy=1)
        Product.objects.create(title='Fanta', qty=4, price=5, price_buy=1)
        Product.objects.create(title='Coca', qty=0, price=2, price_buy=1)
        Product.objects.create(title='Test', qty=2, price=3, price_buy=2)
        

    def test_products(self):
        coca_cola = Product.objects.get(title='Coca Cola')
        self.assertEqual(coca_cola.qty, 5)
