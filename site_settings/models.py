from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.db.models import Sum, Q
from django.contrib.auth.models import User

from .constants import BANKS, CURRENCY


class DefaultBasicModel(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    costum_ordering = models.IntegerField(default=1)

    class Meta:
        abstract = True


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


class Store(models.Model):
    title = models.CharField(unique=True, max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Country(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.title


class DefaultOrderModel(models.Model):
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL)
    date_expired = models.DateTimeField(auto_created=True)
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    taxes = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    discount = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    is_paid = models.BooleanField(default=False)
    printed = models.BooleanField(default=False)
    objects = models.Manager()

    class Meta:
        abstract = True


class DefaultOrderItemModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    qty = models.PositiveIntegerField(default=1)
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    discount_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0)

    class Meta:
        abstract = True


class PaymentOrders(DefaultOrderModel):
    is_expense = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Επιταγη {self.title}"


@receiver(post_delete, sender=PaymentOrders)
def update_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.content_object
    try:
        get_order.is_paid = False
        get_order.paid_value = 0
        get_order.save()
    except:
        t = ''