from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Q
from django.contrib.auth.models import User


from app_settings.default_models.orders import DefaultOrderModel

from .constants import BANKS
CURRENCY = settings.CURRENCY


class PaymentMethodManager(models.Manager):

    def active(self):
        return super(PaymentMethodManager, self).filter(active=True)

    def active_for_site(self):
        return super(PaymentMethodManager, self).filter(active=True, site_active=True)


class PaymentMethod(models.Model):
    title = models.CharField(unique=True, max_length=100)
    active = models.BooleanField(default=True)
    site_active = models.BooleanField(default=False)
    additional_cost = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    limit_value = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    objects = models.Manager()
    my_query = PaymentMethodManager()

    def __str__(self):
        return self.title

    def tag_additional_cost(self):
        return '%s %s' % (self.additional_cost, CURRENCY)

    def tag_limit_value(self):
        return '%s %s' % (self.limit_value, CURRENCY)


class PaymentOrders(DefaultOrderModel):
    payment_type = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL)
    is_expense = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Επιταγη {self.id}" 
  

@receiver(post_delete, sender=PaymentOrders)
def update_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.content_object
    try:
        get_order.is_paid = False
        get_order.paid_value = 0
        get_order.save()
    except:
        t = ''

class Country(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.title

    


