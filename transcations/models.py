from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from decimal import Decimal
from model_utils import FieldTracker

from inventory_manager.models import *
from site_settings.constants import *
from site_settings.models import PaymentMethod, PaymentOrders, Store
from site_settings.models import DefaultOrderModel, DefaultOrderItemModel


import datetime

User = get_user_model()
CURRENCY = settings.CURRENCY

class BillCategory(models.Model):
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, max_digits=50, decimal_places=2)

    def __str__(self):
        return self.title

    
class Bill(DefaultOrderModel):
    category = models.ForeignKey(BillCategory, null=True, on_delete=models.SET_NULL)
    payment_orders = GenericRelation(PaymentOrders)

    class Meta:
        ordering = ['date_expired',]
    
    def __str__(self):
        return f'{self.category} - {self.title}' if self.category else f'self.title'

    def save(self, *args, **kwargs):
        self.final_value = self.value
        self.paid_value = self.payment_orders.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        if self.is_paid:
            get_value = self.get_remaining_value
            if get_value > 0:
                new_payment_order = PaymentOrders.objects.create(title=f'{self.title}',
                                                         value=self.get_remaining_value,
                                                         payment_method=self.payment_method,
                                                         is_paid=True,
                                                         object_id=self.id,
                                                         content_type=ContentType.objects.get_for_model(self),
                                                         is_expense=True
                                                        )
        super().save(*args, **kwargs)

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'


class Occupation(models.Model):
    title = models.CharField(max_length=64, verbose_name='Απασχόληση')
    notes = models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')

    class Meta:
        verbose_name_plural = "5. Απασχόληση"

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    tag_balance.short_description = 'Υπόλοιπο'

    def __str__(self):
        return self.title


class Person(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονοματεπώνυμο')
    phone = models.CharField(max_length=10, verbose_name='Τηλέφωνο', blank=True)
    phone1 = models.CharField(max_length=10, verbose_name='Κινητό', blank=True)
    date_added = models.DateField(default=timezone.now, verbose_name='Ημερομηνία Πρόσληψης')
    occupation = models.ForeignKey(Occupation, verbose_name='Απασχόληση', on_delete=models.CASCADE)
    store_related = models.ForeignKey(Store, blank=True, null=True, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')
    vacation_days = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "6. Υπάλληλος"

    def save(self, *args, **kwargs):
        get_orders = PayrollInvoice.objects.filter(person=self)
        person_value = get_orders.aggregate(Sum('value'))['value__sum'] if get_orders else 0
        person_paid = get_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if get_orders else 0
        self.balance = person_value - person_paid
        super(Person, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    tag_balance.short_description = 'Υπόλοιπο'

    def calculate_total_days(self):
        vacations = self.vacations.all()  # .all().filter(date_started__year=datetime.date.year(),)
        print(vacations)
        days = vacations.aggregate(Sum('days'))['days__sum'] if vacations else 0
        return days


class PayrollInvoiceManager(models.Manager):
    def invoice_per_person(self, instance):
        return super(PayrollInvoiceManager, self).filter(person=instance)

    def not_paid(self):
        return super(PayrollInvoiceManager, self).filter(is_paid=False, active=True)


class Payroll(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, verbose_name='Περιγραφή', blank=True, null=True)
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος', on_delete=models.CASCADE)
    category = models.CharField(max_length=1, choices=PAYROLL_CHOICES, default='1')
    value = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Αξία')
    date_created = models.DateField(auto_now=True)
    date_expired = models.DateField(default=timezone.now, verbose_name='Πληρωμή μέχρι .....')
    paid_value = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Πιστωτικό Υπόλοιπο')
    payment_method = models.CharField(max_length=1, choices=PAYMENT_TYPE, default='1')
    is_paid = models.BooleanField(default=False)
    payorders = GenericRelation(PaymentOrders)
    objects = models.Manager()
    my_query = PayrollInvoiceManager()

    class Meta:
        verbose_name_plural = "7. Εντολές Πληρωμής Υπαλλήλων. "
        ordering = ['is_paid', '-date_expired', ]

    def save(self, *args, **kwargs):
        if self.is_paid:
            get_orders = self.payorders.all()
            get_orders.update(is_paid=True)

        self.paid_value = self.payorders.filter(is_paid=True).aggregate(Sum('value'))[
            'value__sum'] if self.payorders.filter(is_paid=True) else 0
        self.paid_value = self.paid_value if self.paid_value else 0

        if self.paid_value >= self.value:
            self.is_paid = True

        if self.is_paid and self.paid_value < self.value:
            new_order = PaymentOrders.objects.create(payment_type=self.payment_method,
                                                     value=self.value - self.paid_value,
                                                     is_paid=True,
                                                     content_type=ContentType.objects.get_for_model(PayrollInvoice),
                                                     object_id=self.id,
                                                     date_expired=self.date_expired,
                                                     )
        super(PayrollInvoice, self).save(*args, **kwargs)
        person = self.person
        person.save()

    def __str__(self):
        return '%s %s' % (self.date_expired, self.person.title)

    def tag_paid_value(self):
        return '%s %s' % (self.paid_value, CURRENCY)

    tag_paid_value.short_description = 'Πληρωμένη Αξία'

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    tag_value.short_description = 'Αξία Παραστατικού'

    def tag_is_paid(self):
        return "Is Paid" if self.is_paid else "Not Paid"

    def get_remaining_value(self):
        return self.value - self.paid_value

    def tag_remaining_value(self):
        return '%s %s' % (self.get_remaining_value(), CURRENCY)


@receiver(pre_delete, sender=Payroll)
def update_on_delete_payrolls(sender, instance, *args, **kwargs):
    get_orders = instance.payorders.all()
    for order in get_orders:
        order.delete()


@receiver(pre_delete, sender=Payroll)
def update_person_on_delete(sender, instance, *args, **kwargs):
    person = instance.person
    person.balance -= instance.price - instance.paid_value
    person.save()


class GenericExpenseCategory(models.Model):
    pass

class GenericExpense(DefaultOrderModel):
    pass



class VacationReason(models.Model):
    title = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.title


class Vacation(models.Model):
    status = models.BooleanField(default=False, verbose_name='Ολοκληρώθηκε')
    staff_related = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='vacations')
    date_started = models.DateField()
    date_end = models.DateField()
    reason = models.ForeignKey(VacationReason, blank=True, null=True, on_delete=models.CASCADE)
    notes = models.CharField(max_length=200, blank=True)
    days = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['status', 'date_started', 'date_end']

    def tag_status(self):
        return 'Ολοκληρώθηκε' if self.status else 'Δεν Ολοκληρωθηκε'





