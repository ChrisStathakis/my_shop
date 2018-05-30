from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Sum
from django.utils.translation import pgettext_lazy
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from tinymce.models import HTMLField


# Create your models here.



class Category(models.Model):
    title = models.CharField(unique=True,max_length=70,verbose_name='Τίτλος Κατηγορίας')
    description = models.TextField(null=True,blank=True, verbose_name='Περιγραφή')

    class Meta:
        ordering = ['title']
        verbose_name = "3. Κατηγορίες Αποθήκης"
        verbose_name_plural = '3. Κατηγορίες Αποθήκης'

    def __str__(self):
        return self.title


class TaxesCity(models.Model):
    title = models.CharField(max_length=64,unique=True)

    class Meta:
        verbose_name="ΔΟΥ   "

    def __str__(self):
        return self.title


class Vendor(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=70, verbose_name="'Ονομα")
    afm = models.CharField(max_length=9, blank=True, null=True, verbose_name="ΑΦΜ")
    doy = models.ForeignKey(TaxesCity, verbose_name='Εφορία', null=True, blank=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    phone1 = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    fax = models.CharField(max_length=10, null=True, blank=True, verbose_name="Fax")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")

    site = models.CharField(max_length=40, blank=True, null=True, verbose_name='Site')
    address = models.CharField(max_length=40, null=True, blank=True, verbose_name='Διεύθυνση')
    city = models.CharField(max_length=40, null=True, blank=True, verbose_name='Πόλη')
    zip_code = models.CharField(max_length=40, null=True, blank=True, verbose_name='TK')
    description = models.TextField(null=True, blank=True, verbose_name="Περιγραφή")
    date_added = models.DateField(default=timezone.now)
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    # managing deposits
    remaining_deposit = models.DecimalField(default=0, decimal_places=2, max_digits=100,
                                            verbose_name='Υπόλοιπο προκαταβολών')
    balance = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name="Υπόλοιπο")
    payment_orders = GenericRelation(PaymentOrders)

    class Meta:
        verbose_name_plural = '9. Προμηθευτές'
        ordering = ['title', ]
        
    def save(self, *args, **kwargs):
        orders = self.order_set.all()
        self.balance = orders.aggregate(Sum('total_price'))['total_price__sum'] if orders else 0
        self.balance -= orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
        self.balance -= self.payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] \
        if self.payment_orders.filter(is_paid=True) else 0
        self.remaining_deposit = self.payment_orders.filter(is_paid=False).aggregate(Sum('value'))['value__sum'] \
        if self.payment_orders.filter(is_paid=False) else 0
        super(Supply, self).save(*args, **kwargs)

    @staticmethod
    def filter_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        balance_name = request.GET.get('balance_name', None)
        try:
            queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
            queryset = queryset.filter(balance__gte=1) if balance_name else queryset
            queryset = queryset.filter(id__in=vendor_name) if vendor_name else queryset
        except:
            queryset = queryset
        return queryset

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:vendor_detail', args={'dk': self.id})

    def template_tag_remaining_deposit(self):
        return ("{0:.2f}".format(round(self.remaining_deposit, 2))) + ' %s'%(CURRENCY)

    def tag_balance(self):
        return ("{0:.2f}".format(round(self.balance, 2))) + ' %s'%(CURRENCY)

    def tag_deposit(self):
        return "%s %s" % (self.remaining_deposit, CURRENCY)

    def tag_phones(self):
        return '%s' % self.phone if self.phone else ' ' + ', %s' % self.phone1 if self.phone1 else ' '     

    def get_absolute_url_form(self):
        return reverse('edit_vendor_id',kwargs={'dk':self.id})