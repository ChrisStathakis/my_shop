from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import F, Sum, Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
import datetime
from decimal import Decimal

from .managers import RetailOrderManager, RetailOrderItemManager
from accounts.models import CostumerAccount, BillingProfile, Address
from products.models import  Product, SizeAttribute, Gifts
from site_settings.constants import CURRENCY, TAXES_CHOICES
from site_settings.models import DefaultOrderModel, DefaultOrderItemModel
from site_settings.models import PaymentMethod, PaymentOrders, Shipping
from site_settings.constants import CURRENCY, ORDER_STATUS, ORDER_TYPES
from carts.models import Cart, CartItem, Coupons, CartGiftItem

from .tools import update_warehouse, payment_method_default

RETAIL_TRANSCATIONS, PRODUCT_ATTRITUBE_TRANSCATION  = settings.RETAIL_TRANSCATIONS, settings.PRODUCT_ATTRITUBE_TRANSCATION 


class RetailOrder(DefaultOrderModel):
    billing_profile = models.OneToOneField(BillingProfile, blank=True, null=True, on_delete=models.SET_NULL)
    address_profile = models.OneToOneField(Address, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default='1')
    order_type = models.CharField(max_length=1, choices=ORDER_TYPES, default='r')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                     verbose_name='Συνολικό Κόστος Παραγγελίας')
    costumer_account = models.ForeignKey(CostumerAccount,
                                         blank=True,
                                         null=True,
                                         verbose_name='Costumer',
                                         on_delete=models.SET_NULL)
    seller_account = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='seller')
    #  eshop info only
    shipping = models.ForeignKey(Shipping, null=True, blank=True, on_delete=models.SET_NULL)
    shipping_cost = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    payment_cost = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    day_sent = models.DateTimeField(blank=True, null=True)
    eshop_order_id = models.CharField(max_length=10, blank=True, null=True)
    eshop_session_id = models.CharField(max_length=50, blank=True, null=True)

    my_query = RetailOrderManager()
    objects = models.Manager()

    cart_related = models.OneToOneField(Cart, blank=True, null=True, on_delete=models.SET_NULL)
    coupons = models.ManyToManyField(Coupons, blank=True)
    order_related = models.ForeignKey('self', blank=True, null=True, on_delete = models.CASCADE)
    payorders = GenericRelation(PaymentOrders)

    class Meta:
        verbose_name_plural = '1. Παραστατικά Πωλήσεων'
        verbose_name = 'Πώληση'
        ordering = ['-timestamp']

    def __str__(self):
        return self.title if self.title else 'order'

    def save(self, *args, **kwargs):
        order_items = self.order_items.all()
        self.count_items = order_items.count() if order_items else 0
        # self.check_coupons()
        self.update_order()
        self.final_value = self.shipping_cost + self.payment_cost + self.value - self.discount
        self.paid_value = self.payorders.all().aggregate(Sum('value'))['value__sum'] if self.payorders else 0
        self.paid_value = self.paid_value if self.paid_value else 0
        if self.status in ['7', '8']:
            self.is_paid = True
        if self.is_paid and self.paid_value < self.final_value and not self.order_type in ['e', 'r']:
            print('paid section')
            new_order = PaymentOrders.objects.create(payment_method=self.payment_method,
                                                     value=self.final_value - self.paid_value,
                                                     is_paid=True,
                                                     content_type=ContentType.objects.get_for_model(RetailOrder),
                                                     object_id=self.id,
                                                     date_expired=datetime.datetime.now(),
                                                     is_expense=False,
                                                     )
            self.paid_value += new_order.value
        super(RetailOrder, self).save(*args, **kwargs)
        if self.costumer_account:
            self.costumer_account.save()
        if self.order_type in ['b', 'd']:
            self.payorders.all().update(is_expense=True)

    def update_order(self):
        items = self.order_items.all()
        self.value = items.aggregate(Sum('total_value'))['total_value__sum'] if items else 0
        self.total_cost = items.aggregate(Sum('total_cost_value'))['total_cost_value__sum'] if items else 0


    def check_coupons(self):
        try:
            total_value = 0
            active_coupons = Coupons.my_query.active_date(date=datetime.datetime.now())
            for coupon in self.coupons.all():
                if coupon in active_coupons :
                    if self.value > coupon.cart_total_value:
                        total_value += coupon.discount_value if coupon.discount_value else \
                        (coupon.discount_percent/100)*self.value if coupon.discount_percent else 0
            self.discount = total_value
        except:
            self.discount = 0

    def get_report_url(self):
        return reverse('reports:retail_order_detail', kwargs={'pk': self.id})

    def get_dashboard_url(self):
        return reverse('dashboard:eshop_order_edit', kwargs={'pk': self.id})

    def get_dashboard_print_url(self):
        return reverse('dashboard:print_invoice', kwargs={'pk': self.id})

    def is_sale(self):
        return True if self.order_type in ['r', 'e'] else False

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)
    tag_final_value.short_description = 'Τελική Αξία'

    def tag_paid_value(self):
        return '%s %s' % (self.paid_value, CURRENCY)
    tag_paid_value.short_description = 'Αποπληρωμένο Πόσο'

    def tag_cost_value(self):
        return '%s %s' % (self.total_cost, CURRENCY)

    def tag_discount(self):
        return '%s %s' %(self.discount, CURRENCY)

    @property
    def get_total_taxes(self):
        choice = 24
        for ele in TAXES_CHOICES:
            if ele[0] == self.taxes:
                choice = ele[1]
        return self.final_value * (Decimal(choice)/100)

    def tag_total_taxes(self):
        return '%s %s' % (self.get_total_taxes, CURRENCY)

    def tag_clean_value(self):
        return '%s %s' % (self.final_value - self.get_total_taxes, CURRENCY)

    def tag_shipping_value(self):
        return '%s %s' % (self.shipping_cost, CURRENCY)

    def tag_payment_value(self):
        return '%s %s' % (self.payment_cost, CURRENCY)

    @property
    def get_order_items(self):
        return self.order_items.all()

    @property
    def tag_remain_value(self):
        return '%s %s' % (round(self.final_value - self.paid_value, 2), CURRENCY)
    
    def tag_status(self):
        return f'{self.get_status_display()}'

    def tag_order_type_and_status(self):
        text = f'{self.get_order_type_display()} - {self.get_status_display()}' if self.order_type in ['e', 'r'] else f'{self.get_order_type_display()}'
        back_color = 'success' if self.order_type in ['e', 'r'] and self.status in ['4','7', '8'] else 'info' if self.order_type in ['e', 'r'] else 'danger' if self.order_type == 'c' else 'warning'
        return mark_safe('<td class="%s">%s</td>' %(back_color, text))

    def tag_costumer(self):
        return self.costumer_account

    def tag_seller_point(self):
        return self.seller_account.username if self.seller_account else 'No data'

    def is_printed(self):
        return 'Printed' if self.printed else 'Not Printed'
    
    def tag_phones(self):
        if self.billing_profile:
            my_profile = self.billing_profile
            return 'CellPhone.. %s, Phone %s' % (my_profile.cellphone,
                                                 my_profile.phone) if my_profile.phone else my_profile.cellphone
        return 'No Phones added'

    def tag_fullname(self):
        if self.costumer_account:
            if not self.costumer_account.user:
                return f'{self.costumer_account.first_name}'
            if self.costumer_account.user:
                return f'Account: {self.costumer_account.user.username}'
        if self.billing_profile:
            return f'{self.billing_profile.first_name} {self.billing_profile.last_name}'
        return 'No name added'
    
    def tag_full_address(self):
        if self.address_profile:
            return f'{self.address_profile.address_line_1}, City: {self.address_profile.city}'
        return 'No address added'

    @staticmethod
    def eshop_orders_filtering(request, queryset):
        search_name = request.GET.get('search_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        printed_name = request.GET.get('printed_name', None)
        status_name = request.GET.getlist('status_name', None)
        payment_name = request.GET.getlist('payment_name', None)
        queryset = queryset.filter(printed=False) if printed_name else queryset
        queryset = queryset.filter(payment_method__id__in=payment_name) if payment_name else queryset
        queryset = queryset.filter(status__in=status_name) if status_name else queryset
        queryset = queryset.filter(is_paid=False) if paid_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(cellphone__icontains=search_name) |
                                   Q(address__icontains=search_name) |
                                   Q(city__icontains=search_name) |
                                   Q(zip_code__icontains=search_name) |
                                   Q(phone__icontains=search_name) |
                                   Q(first_name__icontains=search_name) |
                                   Q(last_name__icontains=search_name)
                                   ).distinct() if search_name else queryset
        
        return queryset
    
    @staticmethod
    def estimate_shipping_and_payment_cost(cart, payment_method, shipping_method):
        payment_cost = payment_method.estimate_additional_cost(cart.value) if payment_method else 0
        shipping_cost = shipping_method.estimate_additional_cost(cart.value) if shipping_method else 0
        return [shipping_cost, payment_cost]

    @staticmethod
    def new_order_payment_and_costumer():
        payments = PaymentMethod.objects.filter(title='Cash')
        payment = payments.first() if payments.exists() else PaymentMethod.objects.create(title='Cash')
        costumer, create = CostumerAccount.objects.get_or_create(first_name='Costumer', last_name='Account')
        return payment, costumer

    @staticmethod
    def create_order_from_cart(form, cart, cart_items):
        payment_method = form.cleaned_data.get('payment_method', None)
        shipping_method = form.cleaned_data.get('shipping_method', None)
        shipping_cost, payment_cost = RetailOrder.estimate_shipping_and_payment_cost(cart,
                                                                                     payment_method,
                                                                                     shipping_method
                                                                                     )
        billing_profile, created = BillingProfile.objects.get_or_create(cart=cart)
        billing_profile.email=form.cleaned_data.get('email')
        billing_profile.first_name=form.cleaned_data.get('first_name')
        billing_profile.last_name=form.cleaned_data.get('last_name')
        billing_profile.cellphone=form.cleaned_data.get('cellphone')
        billing_profile.phone=form.cleaned_data.get('phone', None)
        billing_profile.costumer_submit=form.cleaned_data.get('agreed')
        billing_profile.save()
        address_profile, created = Address.objects.get_or_create(billing_profile=billing_profile)
        address_profile.address_line_1=form.cleaned_data.get('address')
        address_profile.city=form.cleaned_data.get('city')
        address_profile.postal_code=form.cleaned_data.get('zip_code')
        address_profile.save()                                   
        new_order = RetailOrder.objects.create(order_type='e',
                                               title=f'EshopOrder1{cart.id}',
                                               payment_method=form.cleaned_data.get('payment_method'),
                                               shipping=form.cleaned_data.get('shipping_method'),
                                               shipping_cost=shipping_cost,
                                               payment_cost=payment_cost,
                                               billing_profile=billing_profile,
                                               address_profile=address_profile,
                                               eshop_session_id=cart.id_session,
                                               notes=form.cleaned_data.get('notes'),
                                               cart_related=cart,
                                               )
        if cart.user:
            new_order.costumer_account = CostumerAccount.objects.get(user=cart.user)
            new_order.save()
            billing_profile.user = cart.user
            billing_profile.save()
        for item in cart_items:
            if item.characteristic:
                order_item = RetailOrderItem.objects.create(title=item.product_related,
                                                            order=new_order,
                                                            cost=item.product_related.price_buy,
                                                            value=item.price,
                                                            qty=item.qty,
                                                            discount_value=item.price_discount,
                                                            size=item.characteristic,
                                                            )
                    

            else:
                order_item = RetailOrderItem.objects.create(title=item.product_related,
                                                            order=new_order,
                                                            cost=item.product_related.price_buy,
                                                            value=item.price,
                                                            qty=item.qty,
                                                            discount_value=item.price_discount,
                                                            )
            order_item.update_warehouse('remove', item.qty)
        new_order.update_order()
        cart.is_complete = True
        cart.save()
        return new_order


@receiver(post_delete, sender=RetailOrder)
def update_on_delete_retail_order(sender, instance, *args, **kwargs):
    payments_order = instance.payorders.all()
    for order in payments_order:
        order.delete()
    for order in instance.order_items.all():
        order.delete()


class RetailOrderItem(DefaultOrderItemModel):
    order = models.ForeignKey(RetailOrder, on_delete=models.CASCADE, related_name='order_items')
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    title = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    #  warehouse_management
    is_find = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False)
    size = models.ForeignKey(SizeAttribute, blank=True, null=True, on_delete=models.SET_NULL)
    total_value = models.DecimalField(max_digits=20, decimal_places=0, default=0, help_text='qty*final_value')
    total_cost_value = models.DecimalField(max_digits=20, decimal_places=0, default=0, help_text='qty*cost')
    my_query = RetailOrderItemManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '2. Προϊόντα Πωληθέντα'
        ordering = ['-order__timestamp', ]

    def __str__(self):
        return self.title.title

    def save(self, *args, **kwargs):
        self.final_value = self.discount_value if self.discount_value > 0 else self.value
        self.total_value = self.final_value*self.qty
        self.total_cost_value = self.cost*self.qty
        super(RetailOrderItem, self).save(*args, **kwargs)

    def update_warehouse(self, transcation_type, qty):
        update_warehouse(self, transcation_type, qty)

    def update_order(self):
        self.order.save()

    def get_clean_value(self):
        return self.final_value * (100-self.order.taxes/100)

    @property
    def get_total_value(self):
        return round(self.final_value*self.qty, 2)

    @property
    def get_total_cost_value(self):
        return round(self.cost * self.qty, 2)

    def tag_clean_value(self):
        return '%s %s' % (self.get_clean_value(), CURRENCY)

    def tag_total_value(self):
        return '%s %s' % (self.get_total_value, CURRENCY)
    tag_total_value.short_description = 'Συνολική Αξία'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία Μονάδας'

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)
    
    def tag_found(self):
        return 'Found' if self.is_find else 'Not Found'

    def tag_total_taxes(self):
        return '%s %s' %(round(self.value*self.qty*(Decimal(self.order.taxes)/100), 2), CURRENCY)

    def type_of_order(self):
        return self.order.order_type

    def template_tag_total_price(self):
        return "{0:.2f}".format(round(self.value*self.qty,2)) + ' %s'%(CURRENCY)

    def price_for_vendor_page(self):
        #returns silimar def for price in vendor_id page
        return self.value

    def absolute_url_vendor_page(self):
        return reverse('retail_order_section', kwargs={'dk': self.order.id})

    @staticmethod
    def check_if_exists(order, product):
        exists = RetailOrderItem.objects.filter(title=product, order=order)
        return exists.first() if exists else None

    @staticmethod
    def add_item(self, order_id, product_id, qty):
        order = get_object_or_404(RetailOrder, id=order_id)
        product = get_object_or_404(Product, id=product_id)
        instance, created = RetailOrderItem.objects.get_or_create(order=order,
                                                                  product=product
                                                                  )
        if created:
            instance.qty = qty
        else:
            instance.qty += 1
        instance.save()

    @staticmethod
    def barcode(request, instance):
        barcode = request.GET.get('barcode')
        print(barcode)
        try:
            barcode_string = barcode.split(' ')
            if len(barcode_string) == 1:
                product_id = barcode_string[0]
                RetailOrderItem.create_or_edit_item(instance, Product.objects.get(id=product_id), 1, 'ADD')
        except:
            messages.warning(request, 'No Product Found')

    @staticmethod
    def create_or_edit_item(order, product, qty, transation_type):
        instance, created = RetailOrderItem.objects.get_or_create(order=order, title=product)
        if transation_type == 'ADD':
            if not created:
                instance.qty += qty
            else:
                instance.qty = qty
                instance.value = product.price
                instance.discount_value=product.price_discount
                instance.cost = product.price_buy
        if transation_type == 'REMOVE':
            instance.qty -= qty
            instance.qty = 1 if instance.qty <= 0 else instance.qty
        instance.save()
        if transation_type == 'DELETE':
            instance.delete()
        order.save()
'''
class OrderProfile(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    zipcode = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    country = models.CharField(max_length=1, blank=True)
    order_type = models.CharField(max_length=1)
    order_related = models.ForeignKey(RetailOrder)
    
    class Meta:
        unique_together = ['order_related', 'order_type']
'''


def create_destroy_title():
    last_order = RetailOrderItem.objects.all().last()
    if last_order:
        number = int(last_order.id)+1
        return 'ΚΑΤ'+ str(number)
    else:
        return 'ΚΑΤ1'


class GiftRetailItem(models.Model):
    product_related = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_related = models.ForeignKey(RetailOrder, on_delete=models.CASCADE, related_name='gifts')
    cart_related = models.ForeignKey(Cart, on_delete=models.SET_NULL, blank=True, null=True)
    qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.cart_related}'

    @staticmethod
    def create_gifts(cart, order, cart_items, gifts):
        if gifts:
            for gift in gifts:
                new_gift = GiftRetailItem.objects.create(product_related=gift.product_related,
                                                        order_related=order,
                                                        cart_related=gift.cart_related,
                                                        qty=gift.qty
                                                        )

    def check_retail_order(order, cart=None):
        gifts = order.gifts.all()
        gifts.delete()
        items = order.order_items.all()
        for item in items:
            can_be_gift = Gifts.objects.filter(product_related=item.title)
            if can_be_gift.exists:
                for gift in can_be_gift:
                    new_gift = GiftRetailItem.objects.create(product_related=gift.products_gift,
                                                             order_related=order,
                                                             qty=item.qty,

                                                            )
                    if cart:
                        new_gift.cart_related = cart
                        new_gift.save()
