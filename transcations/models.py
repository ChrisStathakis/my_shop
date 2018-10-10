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
from .managers import BillCategoryManager, ExpenseCategoryManager, PersonManager, OccupationManager, GeneralManager

import datetime

User = get_user_model()
CURRENCY = settings.CURRENCY


class BillCategory(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, max_digits=50, decimal_places=2)
    objects = models.Manager()
    my_query = BillCategoryManager()

    def __str__(self):
        return self.title

    def get_dashboard_url(self):
        return reverse('billings:bill_cate_detail', kwargs={'pk': self.id})

    def get_report_url(self):
        return reverse('billings:report')

    def update_balance(self):
        queryset = self.bills.all()
        value = queryset.aggregate(Sum('final_value'))['final_value__sum']  if queryset else 0
        paid_value = queryset.aggregate(Sum('paid_value'))['paid_value__sum'] if queryset else 0
        self.balance = value - paid_value
        self.save()

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset

    
class Bill(DefaultOrderModel):
    category = models.ForeignKey(BillCategory, null=True, on_delete=models.SET_NULL, related_name='bills')
    payment_orders = GenericRelation(PaymentOrders)
    objects = models.Manager()
    my_query = GeneralManager()

    class Meta:
        ordering = ['-date_expired',]
    
    def __str__(self):
        return f'{self.category} - {self.title}' if self.category else f'self.title'

    def tag_model(self):
        return f'Bill- {self.category.title}' 

    def save(self, *args, **kwargs):
        if not self.is_paid:
            for ele in self.payment_orders.all():
                ele.delete()
        self.final_value = self.value
        self.paid_value = self.payment_orders.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        super().save(*args, **kwargs)
        if self.is_paid:
            get_value = self.get_remaining_value()
            if get_value > 0:
                new_payment_order = PaymentOrders.objects.create(title=f'{self.title}',
                                                         value=self.get_remaining_value(),
                                                         payment_method=self.payment_method,
                                                         is_paid=True,
                                                         object_id=self.id,
                                                         content_type=ContentType.objects.get_for_model(self),
                                                         is_expense=True
                                                        )
        self.category.update_balance()

    def get_dashboard_url(self):
        return reverse('billings:edit_page', kwargs={'mymodel':'bill', 'pk': self.id, 'slug':'edit'})

    def get_paid_url(self):
        return reverse('billings:edit_page', kwargs={'mymodel':'bill', 'pk': self.id, 'slug': 'paid'})

    def get_delete_url(self):
        return reverse('billings:edit_page', kwargs={'mymodel':'bill', 'pk': self.id, 'slug':'delete'})
    
    def get_dashboard_save_as_url(self):
        return reverse('billings:save_as_view', kwargs={'pk': self.id, 'slug': 'bill'})

    def get_dashboard_list_url(self):
        return reverse('billings:bill_list')

    def update_category(self):
        self.category.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    @staticmethod
    def filters_data(request, queryset):
        paid_name = request.GET.getlist('paid_name', None)
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        queryset = queryset.filter(is_paid=True) if 'paid' in paid_name else queryset.filter(is_paid=False)\
            if 'not_paid' in paid_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name)|
                                   Q(category__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


class Occupation(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, verbose_name='Απασχόληση')
    notes = models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')

    objects = models.Manager()
    my_query = OccupationManager()

    class Meta:
        verbose_name_plural = "5. Απασχόληση"

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    tag_balance.short_description = 'Υπόλοιπο'

    def get_dashboard_url(self):
        return reverse('billings:occup_detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.title

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class Person(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονοματεπώνυμο')
    phone = models.CharField(max_length=10, verbose_name='Τηλέφωνο', blank=True)
    phone1 = models.CharField(max_length=10, verbose_name='Κινητό', blank=True)
    date_added = models.DateField(default=timezone.now, verbose_name='Ημερομηνία Πρόσληψης')
    occupation = models.ForeignKey(Occupation, null=True, verbose_name='Απασχόληση', on_delete=models.SET_NULL)
    store_related = models.ForeignKey(Store, blank=True, null=True, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=50, decimal_places=2, default=0, verbose_name='Υπόλοιπο')
    vacation_days = models.IntegerField(default=0)

    objects = models.Manager()
    my_query = PersonManager()

    class Meta:
        verbose_name_plural = "6. Υπάλληλος"

    def update_balance(self):
        queryset = self.person_invoices.all()
        value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.aggregate(Sum('paid_value'))['paid_value__sum'] if queryset else 0
        diff = value - paid_value
        self.balance = diff
        self.save()

    def __str__(self):
        return self.title

    def tag_balance(self):
        return '%s %s' % (self.balance, CURRENCY)

    def get_dashboard_url(self):
        return reverse('billings:person_detail', kwargs={'pk': self.id})
    tag_balance.short_description = 'Υπόλοιπο'

    def calculate_total_days(self):
        vacations = self.vacations.all()  # .all().filter(date_started__year=datetime.date.year(),)
        print(vacations)
        days = vacations.aggregate(Sum('days'))['days__sum'] if vacations else 0
        return days

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        occup_name = request.GET.getlist('occup_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(occupation__id__in=occup_name) if occup_name else queryset
        return queryset


class PayrollInvoiceManager(models.Manager):
    def invoice_per_person(self, instance):
        return super(PayrollInvoiceManager, self).filter(person=instance)

    def not_paid(self):
        return super(PayrollInvoiceManager, self).filter(is_paid=False)


class Payroll(DefaultOrderModel):
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος', on_delete=models.CASCADE, related_name='person_invoices')
    category = models.CharField(max_length=1, choices=PAYROLL_CHOICES, default='1')
    payment_orders = GenericRelation(PaymentOrders)
    objects = models.Manager()
    my_query = GeneralManager()

    class Meta:
        ordering = ['is_paid', '-date_expired', ]

    def tag_model(self):
        return f'Payroll - {self.person.title}'

    def save(self, *args, **kwargs):
        self.final_value = self.value
        if not self.is_paid:
            for ele in self.payment_orders.all():
                ele.delete()
        self.paid_value = self.payment_orders.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        super(Payroll, self).save(*args, **kwargs)
        if self.is_paid:
            get_value = self.get_remaining_value()
            if get_value > 0:
                new_payment_order = PaymentOrders.objects.create(title=f'{self.title}',
                                                         value=self.get_remaining_value(),
                                                         payment_method=self.payment_method,
                                                         is_paid=True,
                                                         object_id=self.id,
                                                         content_type=ContentType.objects.get_for_model(self),
                                                         is_expense=True
                                                        )
        self.person.save()

    def __str__(self):
        return '%s %s' % (self.date_expired, self.person.title)
    
    def get_dashboard_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'edit', 'mymodel':'payroll'})

    def get_paid_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'paid', 'mymodel':'payroll'})

    def get_delete_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'delete', 'mymodel':'payroll'})
    
    def get_dashboard_save_as_url(self):
        return reverse('billings:save_as_view', kwargs={'pk': self.id, 'slug': 'payroll'})

    def get_dashboard_list_url(self):
        return reverse('billings:payroll_list')

    def update_category(self):
        self.person.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    def tag_paid_value(self):
        return '%s %s' % (self.paid_value, CURRENCY)

    tag_paid_value.short_description = 'Πληρωμένη Αξία'

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    tag_value.short_description = 'Αξία Παραστατικού'

    def tag_is_paid(self):
        return "Is Paid" if self.is_paid else "Not Paid"

    def get_remaining_value(self):
        return self.final_value - self.paid_value

    def tag_remaining_value(self):
        return '%s %s' % (self.get_remaining_value(), CURRENCY)

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        person_name = request.GET.getlist('person_name', None)
        occup_name = request.GET.getlist('occup_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        cate_name = request.GET.getlist('cate_name', None)

        queryset = queryset.filter(category__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
        queryset = queryset.filter(person__occupation__id__in=occup_name) if occup_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(person__title__icontains=search_name) |
                                   Q(person__occupation__title__icontains=search_name)
                                   ).distict() if search_name else queryset

        return queryset


@receiver(pre_delete, sender=Payroll)
def update_on_delete_payrolls(sender, instance, *args, **kwargs):
    get_orders = instance.payment_orders.all()
    for order in get_orders:
        order.delete()


@receiver(pre_delete, sender=Payroll)
def update_person_on_delete(sender, instance, *args, **kwargs):
    person = instance.person
    person.balance -= instance.final_value - instance.paid_value
    person.save()


class GenericExpenseCategory(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    objects = models.Manager()
    my_query = ExpenseCategoryManager()

    def __str__(self):
        return self.title

    def update_balance(self):
        queryset = self.expenses.all()
        value = queryset.aggregate(Sum('final_value'))['final_value__sum'] if queryset else 0
        paid_value = queryset.aggregate(Sum('paid_value'))['paid_value__sum'] if queryset else 0
        self.balance = value - paid_value
        self.save()

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def get_dashboard_url(self):
        return reverse('billings:expense_cate_detail', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)

        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset

 
class GenericExpense(DefaultOrderModel):
    category = models.ForeignKey(GenericExpenseCategory,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='expenses'
                                 )
    payments_orders = GenericRelation(PaymentOrders)
    objects= models.Manager()
    my_query = GeneralManager()

    def tag_model(self):
        return f'Expenses- {self.category}'
        
    class Meta:
        ordering = ['is_paid', '-date_expired']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.is_paid:
            for payment in self.payments_orders.all():
                payment.delete()
        if self.is_paid:
            get_value = self.get_remaining_value()
            if get_value > 0:
                new_payment_order = PaymentOrders.objects.create(title=f'{self.title}',
                                                                 value=self.get_remaining_value(),
                                                                 payment_method=self.payment_method,
                                                                 is_paid=True,
                                                                 object_id=self.id,
                                                                 content_type=ContentType.objects.get_for_model(self),
                                                                 is_expense=True
                                                                 )

        super().save(*args, **kwargs)
        self.category.update_balance()

    def get_dashboard_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'edit', 'mymodel': 'expense'})

    def get_paid_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'paid', 'mymodel': 'expense'})

    def get_delete_url(self):
        return reverse('billings:edit_page', kwargs={'pk': self.id, 'slug': 'delete', 'mymodel': 'expense'})

    def get_dashboard_save_as_url(self):
        return reverse('billings:save_as_view', kwargs={'pk': self.id, 'slug': 'expense'})

    def get_dashboard_list_url(self):
        return reverse('billings:expenses_list')


    def update_category(self):
        self.category.update_balance()

    def destroy_payments(self):
        queryset = self.payment_orders.all()
        for payment in queryset:
            payment.delete()

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(category__id__in=cate_name) if category_name else queryset
        queryset = queryset.filter(is_paid=True) if paid_name == 'paid' else queryset.filter(is_paid=False) if paid_name == 'not_paid' else queryset
        return queryset
    
    
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





