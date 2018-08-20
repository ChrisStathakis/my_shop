from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import F, Sum, Q
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Sum
from django.utils.translation import pgettext_lazy
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.contrib import messages
from mptt.models import MPTTModel, TreeForeignKey
from tinymce.models import HTMLField
from site_settings.models import DefaultOrderModel, DefaultOrderItemModel
from site_settings.tools import estimate_date_start_end_and_months
from site_settings.constants import WAREHOUSE_ORDER_TYPE
from decimal import Decimal

WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS

def upload_image(instance, filename):
    return f'/warehouse_images/{instance.title}/{filename}'


def validate_file(value):
    if value.file.size > 1024*1024*0.5:
        raise ValidationError('this file is bigger than 0.5mb')
    return value


# Create your models here.

from site_settings.constants import TAXES_CHOICES, CURRENCY, UNIT
from site_settings.models import PaymentOrders, PaymentMethod


class Category(models.Model):
    title = models.CharField(unique=True,max_length=70,verbose_name='Τίτλος Κατηγορίας')
    description = models.TextField(null=True,blank=True, verbose_name='Περιγραφή')

    class Meta:
        ordering = ['title']
        verbose_name = "3. Κατηγορίες Αποθήκης"
        verbose_name_plural = '3. Κατηγορίες Αποθήκης'

    def __str__(self):
        return self.title

    def get_absolute_admin_url(self):
        return reverse('dashboard:category_detail', kwargs={'pk': self.id})


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
        self.balance = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders else 0
        self.balance -= orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
        # self.balance -= self.payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        self.remaining_deposit = self.payment_orders.filter(is_paid=False).aggregate(Sum('value'))['value__sum'] if self.payment_orders.filter(is_paid=False) else 0
        super(Vendor, self).save(*args, **kwargs)
    

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
        return ("{0:.2f}".format(round(self.remaining_deposit, 2))) + ' %s' % (CURRENCY)

    def tag_balance(self):
        return ("{0:.2f}".format(round(self.balance, 2))) + ' %s' % (CURRENCY)

    def tag_deposit(self):
        return "%s %s" % (self.remaining_deposit, CURRENCY)

    def tag_phones(self):
        return '%s' % self.phone if self.phone else ' ' + ', %s' % self.phone1 if self.phone1 else ' '     

    def get_absolute_url_form(self):
        return reverse('edit_vendor_id', kwargs={'dk':self.id})


class OrderManager(models.Manager):
    def pending_orders(self):
        return super(OrderManager, self).filter(is_paid=False).order_by('day_created')

    def complete_orders(self):
        return super(OrderManager, self).filter(is_paid=True).order_by('day_created')


class Order(DefaultOrderModel):
    vendor = models.ForeignKey(Vendor, verbose_name="Προμηθευτής", on_delete=models.CASCADE)
    total_price_no_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2,
                                                  verbose_name="Καθαρή Αξία")
    total_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία έκπτωσης")
    total_price_after_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2,
                                                     verbose_name="Αξία μετά την έκπτωση")
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    total_taxes = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Φ.Π.Α")
    order_type = models.CharField(default=1, max_length=1, choices=WAREHOUSE_ORDER_TYPE)

    objects = models.Manager()
    my_query = OrderManager()
    payment_orders = GenericRelation(PaymentOrders)
    update_warehouse= models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "1. Τιμολόγια"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        order_items= self.order_items.all()
        self.total_price_no_discount = order_items.aggregate(total=Sum(F('qty')*F('value'), output_field=models.FloatField()))['total'] if order_items else 0
        self.total_price_after_discount = order_items.aggregate(total=Sum(F('qty')*F('final_value'), output_field=models.DecimalField()))['total'] if order_items else 0 
        self.total_taxes = (self.total_price_after_discount - self.total_discount) * (Decimal(self.get_taxes_modifier_display()) / 100)
        self.final_value = self.total_price_after_discount + self.total_taxes -self.total_discount
        if self.is_paid:
            get_orders = self.payment_orders.all()
            get_orders.update(is_paid=True)
        self.paid_value = self.payment_orders.filter(is_paid=True).aggregate(Sum('value'))[
            'value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        self.paid_value = self.paid_value if self.paid_value else 0

        if self.paid_value >= self.final_value and self.paid_value > 0.5:
            self.is_paid = True

        '''
        if self.is_paid and self.paid_value < self.final_value:
            get_diff = self.total_price - self.paid_value
            new_payment = PaymentOrders.objects.create(date_expired=self.day_created,
                                                       value=get_diff,
                                                       payment_type=self.payment_method,
                                                       is_paid=True,
                                                       title='%s' % self.code if self.code else 'Τιμολόγιο %s' % self.id,
                                                       content_type=ContentType.objects.get_for_model(Order),
                                                       object_id=self.id
                                                       )
        '''

        super(Order, self).save(*args, **kwargs)
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            self.update_warehouse()


    def update_warehouse(self):
        self.vendor.save()
        

    @staticmethod
    def filter_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        balance_name = request.GET.get('balance_name', None)
        paid_name = request.GET.get('paid_name', None)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
        payment_name = request.GET.getlist('payment_name', None)
        try:
            queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
            queryset = queryset.filter(Q(title__icontains=search_name) |
                                       Q(vendor__title__icontains=search_name)
                                       ).dinstict() if search_name else queryset
            queryset = queryset.filter(date_created__range=[date_start, date_end]) if date_start else queryset
            queryset = queryset.filter(is_paid=True) if paid_name == 'paid' else queryset.filter(is_paid=False) \
                if paid_name == 'not_paid' else queryset
            queryset = queryset.filter(total_price__gte=balance_name) if balance_name else queryset
            queryset = queryset.filter(payment_name__id__in=payment_name) if payment_name else queryset
        except:
            queryset = queryset
        return queryset

    def images_query(self):
        return self.warehouseorderimage_set.all()

    def absolute_url_order(self):
        return reverse('order_edit_main', kwargs={'dk': self.id})

    @property
    def get_remaining_value(self):
        return self.final_value - self.paid_value

    def tag_remaining_value(self):
        return '%s %s' % (self.get_remaining_value, CURRENCY)

    def tag_paid_value(self):
        return '%s %s' % (self.paid_value, CURRENCY)
    tag_paid_value.short_description = 'Πληρωμένη Αξία'

    def tag_is_paid(self):
        return 'Is Paid' if self.is_paid else 'Not Paid'

    def tag_first_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_discount(self):
        return '%s %s' % (self.total_discount, CURRENCY)

    def tag_clean_value(self):
        return f'{self.total_price_after_discount} {CURRENCY}'
    tag_clean_value.short_description = 'Αξία Μετά την έκπτωση'

    def tag_total_taxes(self):
        return f'{self.total_taxes} {CURRENCY}'    

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_form_remain_value(self):
        return True if self.get_remaining_value > 0 else False


class WarehouseOrderImage(models.Model):
    order_related = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_image, null=True, validators=[validate_file, ])
    is_first = models.BooleanField(default=True)

    def __str__(self):
        return '%s-%s' % (self.order_related.code, self.id)


class OrderItem(DefaultOrderItemModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', verbose_name='Προϊόν',
                                on_delete=models.CASCADE,
                                null=True,
                                )
    unit = models.CharField(max_length=1, choices=UNIT, default='1')
    taxes = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    size = models.ForeignKey('products.SizeAttribute', verbose_name='Size', null=True, blank=True, on_delete=models.CASCADE)
    total_clean_value = models.DecimalField(default=0, max_digits=15, decimal_places=2,
                                            verbose_name='Συνολική Αξία χωρίς Φόρους')
    total_value_with_taxes = models.DecimalField(default=0, max_digits=14, decimal_places=2,
                                                 verbose_name='Συνολική Αξία με φόρους')

    class Meta:
        ordering = ['product']
        verbose_name = "Συστατικά Τιμολογίου   "

    def __str__(self):
        return f'{self.product}'

    def save(self, *args, **kwargs):
        self.final_value = Decimal(self.value) * (100-self.discount_value)/100 if self.discount_value > 0 else self.value
        self.total_clean_value = Decimal(self.final_value) * Decimal(self.qty)
        self.total_value_with_taxes = Decimal(self.total_clean_value) * Decimal((100+self.get_taxes_display()) / 100)
        super(OrderItem, self).save(*args, **kwargs)
        self.product.price_buy = self.value
        self.product.order_discount = self.discount_value
        self.product.save()

    def remove_from_order(self, qty):
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            product = self.product
            product.qty -= qty
            product.save()
        self.order.save()

    def quick_add_to_order(self, qty):
        qty = Decimal(qty) if qty else 0
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            product = self.product
            product.qty += qty
            product.save()
        self.order.save()

    @staticmethod
    def add_to_order(request, product, order):
        print(product, order)
        get_order_item = OrderItem.objects.filter(product=product, order=order)
        qty = request.GET.get('qty_%s' % product.id, 0)
        qty = int(qty) if qty else 0
        value = request.GET.get(f'price_{product.id}', product.price_buy)
        discount = request.GET.get(f'discount_{product.id}', product.order_discount)
        discount = Decimal(discount) if discount else 0
        if get_order_item.exists() and qty > 0:
            item = get_order_item.last()
            item.qty += qty
            item.value = value
            item.discount_value = discount
            item.save()
            if WAREHOUSE_ORDERS_TRANSCATIONS:
                product.qty += qty
                product.save()
        elif qty > 0:
            item = OrderItem.objects.create(product=product,
                                            order=order,
                                            qty=qty,
                                            value=value,
                                            discount_value=discount
                                            )
            if WAREHOUSE_ORDERS_TRANSCATIONS:
                product.qty += qty
                product.save()
        else:
            print('wtf')
            messages.warning(request, 'Something goes wrong!')

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_total_clean_value(self):
        return f'{self.total_clean_value} {CURRENCY}'

    def tag_total_final_value(self):
        return '%s %s' % (round(self.total_value_with_taxes), CURRENCY)

    @staticmethod
    def filters_data(request, queryset):
        category_name = request.GET.getlist('category_name', None)
        brand_name = request.GET.getlist('brand_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        queryset = queryset.filter(product__category__id__in=category_name) if category_name else queryset
        queryset = queryset.filter(product__brand__id__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(product_vendor__id__in=vendor_name) if vendor_name else queryset
        return queryset



@receiver(post_delete, sender=OrderItem)
def update_qty_on_delete(sender, instance, *args, **kwargs):
    product, order, self = instance.product,instance.order, instance
    if WAREHOUSE_ORDERS_TRANSCATIONS:
        product.qty -= instance.qty
        product.save()
    self.order.save()


class PreOrder(models.Model):
    STATUS = (('a', 'Active'), ('b', 'Used'))
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=STATUS, default='a')
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

