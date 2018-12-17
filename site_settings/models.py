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
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)
    additional_cost = models.DecimalField(max_digits=6, default=0, decimal_places=2, validators=[validate_positive_decimal, ])
    limit_value = models.DecimalField(default=40, max_digits=6, decimal_places=2,
                                              validators=[validate_positive_decimal, ])
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    first_choice = models.BooleanField(default=False)
    ordering_by = models.IntegerField(default=1)

    class Meta:
        ordering = ['-ordering_by', ]

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

    def tag_limit_value(self):
        return f'{self.limit_value} {CURRENCY}'

    def tag_active(self):
        return 'Active' if self.active else 'No Active'


class PaymentMethod(models.Model):
    title = models.CharField(unique=True, max_length=100)
    active = models.BooleanField(default=True)
    site_active = models.BooleanField(default=False)
    additional_cost = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    limit_value = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    first_choice = models.BooleanField(default=False)
    objects = models.Manager()
    my_query = PaymentMethodManager()

    def __str__(self):
        return self.title

    def tag_additional_cost(self):
        return '%s %s' % (self.additional_cost, CURRENCY)

    def tag_limit_value(self):
        return '%s %s' % (self.limit_value, CURRENCY)

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

    def __str__(self):
        return self.title


class DefaultOrderModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    notes = models.TextField(blank=True, null=True)
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
    printed = models.BooleanField(default=False)
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

    def create_order(self, value):
        PaymentOrders.objects.create(title=f'{self.title}',
                                     value=value,
                                     payment_method=self.payment_method,
                                     is_paid=True,
                                     object_id=self.id,
                                     content_type=ContentType.objects.get_for_model(self),
                                     is_expense=True
                                     )


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


class PaymentOrders(DefaultOrderModel):
    is_expense = models.BooleanField(default=True)
    is_check = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        if self.is_check:
            return f'Check: {self.title}'
        return f"Επιταγη {self.title}"

    def save(self, *args, **kwargs):
        self.final_value = self.value
        super(PaymentOrders, self).save(*args, **kwargs)

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία'

    def get_dashboard_url(self):
        return reverse('inventory:check_order_detail', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        # vendor_name = request.GET.getlist('vendor_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        check_name = request.GET.get('check_name', None)

        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(is_check=True) if check_name == 'check' else queryset.filter(is_check=False) \
            if check_name == 'no_check' else queryset
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False)\
            if 'not_paid' in paid_name else queryset
        return queryset


@receiver(post_delete, sender=PaymentOrders)
def update_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.content_object
    try:
        get_order.is_paid = False
        get_order.paid_value = 0
        get_order.save()
    except:
        t = ''


