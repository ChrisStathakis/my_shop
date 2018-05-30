from django.db import models
from django.contrib.auth.models import User

from products.models import Product

class DefaultOrderModel(models.Model):
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    
    date_expired = models.DateTimeField(auto_created=True)
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    taxes = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    is_paid = models.BooleanField(default=False)
    printed = models.BooleanField(default=False)
    objects = models.Manager()

    class Meta:
        abstract = True



class DefaultOrderItemModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    product_related = models.ForeignKey(Product, on_delete=models.SET_NULL)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    price_discount = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)

    class Meta:
        abstract = True