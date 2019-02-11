from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse
from django.core.exceptions import ValidationError

from .constants import BANKS, CURRENCY
import uuid


def validate_positive_decimal(value):
    if value < 0:
        return ValidationError('This number is negative!')
    return value


class Country(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.title


class PaymentMethodManager(models.Manager):

    def active(self):
        return super(PaymentMethodManager, self).filter(active=True)

    def active_for_site(self):
        return super(PaymentMethodManager, self).filter(active=True, site_active=True)

    def check_orders(self):
        return super(PaymentMethodManager, self).filter(is_check=True)


class ShippingManager(models.Manager):

    def active_and_site(self):
        return super(ShippingManager, self).filter(active=True, for_site=True)
        

class Shipping(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    title = models.CharField(unique=True,
                             max_length=100,
                             verbose_name='Τίτλος'
                             )
    additional_cost = models.DecimalField(max_digits=6,
                                          default=0,
                                          decimal_places=2,
                                          validators=[validate_positive_decimal, ],
                                          verbose_name='Κόστος'
                                          )
    limit_value = models.DecimalField(default=40,
                                      max_digits=6,
                                      decimal_places=2,
                                      validators=[validate_positive_decimal, ],
                                      verbose_name= 'Όριο'
                                      )
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    first_choice = models.BooleanField(default=False, verbose_name='Πρώτη Επιλόγη')
    ordering_by = models.IntegerField(default=1, verbose_name='Σειρα Προτεριότητας')

    class Meta:
        ordering = ['-ordering_by', ]
        verbose_name_plural = 'Τρόποι Μεταφοράς'

    def __str__(self):
        return self.title

    def estimate_additional_cost(self, value):
        if value <= 0 or value >= self.limit_value:
            return 0
        return self.additional_cost

    def tag_active_cost(self):
        return f'{self.additional_cost} {CURRENCY}'

    def tag_active_minimum_cost(self):
        return f'{self.limit_value} {CURRENCY}'

    def tag_additional_cost(self):
        return f'{self.additional_cost} {CURRENCY}'
    tag_additional_cost.short_description = 'Επιπλέον Κόστος'

    def tag_limit_value(self):
        return f'{self.limit_value} {CURRENCY}'

    tag_limit_value.short_description = 'Όριο'

    def tag_active(self):
        return 'Active' if self.active else 'No Active'


class PaymentMethod(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    title = models.CharField(unique=True, max_length=100, verbose_name='Τίτλος')
    site_active = models.BooleanField(default=False, verbose_name='Εμφάνιση στο site')
    additional_cost = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Επιπλέον Κόστος')
    limit_value = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Όριο')
    first_choice = models.BooleanField(default=False)
    objects = models.Manager()
    my_query = PaymentMethodManager()

    class Meta:
        verbose_name_plural = 'Τρόποι Πληρωμής'

    def __str__(self):
        return self.title

    def tag_additional_cost(self):
        return '%s %s' % (self.additional_cost, CURRENCY)

    tag_additional_cost.short_description = 'Επιπλέον Κόστος'

    def tag_limit_value(self):
        return '%s %s' % (self.limit_value, CURRENCY)

    tag_limit_value.short_description = 'Όριο'

    def estimate_additional_cost(self, value):
        if value <= 0 or value >= self.limit_value:
            return 0
        return self.additional_cost


class DefaultBasicModel(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    costum_ordering = models.IntegerField(default=1)

    class Meta:
        abstract = True


class Store(models.Model):
    title = models.CharField(unique=True, max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Κατάστημα'

    def __str__(self):
        return self.title


class DefaultOrderModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')
    title = models.CharField(max_length=150, verbose_name='Τίτλος')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    notes = models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')
    payment_method = models.ForeignKey(PaymentMethod,
                                       null=True,
                                       on_delete=models.PROTECT,
                                       verbose_name='Τρόπος Πληρωμής')
    date_expired = models.DateField(default=timezone.now, verbose_name='Ημερομηνία')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Αξία')
    taxes = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Φόροι')
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Πληρωτέο Ποσό')
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Τελική Αξίσ')
    discount = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Επιπλέον Έκπτωση')
    is_paid = models.BooleanField(default=False, verbose_name='Πληρωμένο?')
    printed = models.BooleanField(default=False, verbose_name='Εκτυπωμένο')
    objects = models.Manager()

    class Meta:
        abstract = True

    def tag_is_paid(self):
        return 'Is Paid' if self.is_paid else 'Not Paid'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'
    tag_value.short_description = 'Αρχική Αξία'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία'

    def tag_paid_value(self):
        return f'{self.paid_value} {CURRENCY}'

    def get_remaining_value(self):
        return self.final_value - self.paid_value

    def tag_payment_method(self):
        return f'{self.payment_method} {CURRENCY}'


class DefaultOrderItemModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, verbose_name='Ημερομηνία Τελευταίας Επεξεργασίας')
    qty = models.PositiveIntegerField(default=1, verbose_name='Ποσότητα')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Άρχικη Αξία')
    discount_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Ποσοστό Έκτωσης')
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Αξία')

    class Meta:
        abstract = True


    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'
    tag_value.short_description = 'Αρχική Αξία'



