from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, F
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib import messages
from django.shortcuts import reverse
from decimal import Decimal
import datetime
# Create your models here.

from site_settings.constants import CURRENCY, RETAIL_TRANSCATIONS
from site_settings.models import DefaultOrderModel, DefaultOrderItemModel
from site_settings.models import PaymentMethod, Shipping
from frontend.models import validate_positive_decimal, CategorySite
from products.models import Product, SizeAttribute, Gifts


class CouponManager(models.Manager):

    def active_coupons(self):
        return super(CouponManager, self).filter(active=True)

    def active_date(self, date,):
        return self.active_coupons().filter(date_created__lte=date, date_end__gte=date)


class Coupons(models.Model):

    '''
    How works, if you pick whole_order, ovverides the products, categories option and the discount goes to cart
    If you dont goes to products related
    If you pick discount_value and discount_percent, value will be picked!
    '''

    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, null=True, max_length=50)
    date_created = models.DateTimeField()
    date_end = models.DateTimeField()
    cart_total_value = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    whole_order = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(CategorySite, blank=True)
    discount_value = models.DecimalField(verbose_name='Discount in Value',
                                         decimal_places=2, max_digits=10, default=0,
                                         help_text='Value gets a priority vs percent. Period'
                                         )
    discount_percent = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    my_query = CouponManager()

    class Meta:
        ordering = ['active', ]
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return self.title

    def get_dashboard_url(self):
        return reverse('dashboard:coupons_edit_view', kwargs={'pk': self.id})

    def tag_cart_total_value(self):
        return f'{self.cart_total_value} {CURRENCY}'

    def tag_value(self):
        if self.discount_value > 0:
            return f'{self.discount_value} {CURRENCY}'
        if self.discount_percent > 0:
            return f'{self.discount_percent} %'
        return 'No data selected'

    def estimate_addiotional_cost(value):
        # not fixed
        value = 0
        return value

    def check_coupon(self, order_type, order, order_items, coupons):
        # order_type 'cart' or 'eshop'
        if self in Coupons.my_query.active_date(date=datetime.datetime.now()):
            if order_type == 'cart':
                if order.value > self.cart_total_value:
                    order.coupon_discount += self.discount_value if self.discount_value else \
                    (self.discount_percent/100)*order.value if self.discount_percent else 0
                if self.categories or self.products:
                    pass
            if order_type == 'eshop':
                order.discount += self.discount_value if self.discount_value else \
                    (self.discount_percent/100)*order.value if self.discount_percent else 0


class CartManager(models.Manager):

    def active_carts(self):
        return super(CartManager, self).filter(active=True)

    def current_cart(self, session_id):
        get_cart = super(CartManager, self).filter(id_session=session_id, active=True)
        return get_cart.last() if get_cart else None


class Cart(models.Model):
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    id_session = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(default=False)
    my_query = CartManager()
    objects = models.Manager()
    shipping_method = models.ForeignKey(Shipping, blank=True, null=True, on_delete=models.SET_NULL)
    payment_method = models.ForeignKey(PaymentMethod, blank=True, null=True, on_delete=models.SET_NULL)
    coupon = models.ManyToManyField(Coupons)
    coupon_discount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[validate_positive_decimal, ])

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return '%s %s' % ('Cart ', self.id)

    def get_dashboard_url(self):
        return reverse('dashboard:cart_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if not self.shipping_method:
            self.shipping_method = Shipping.objects.filter(first_choice=True).last() if Shipping.objects.filter(first_choice=True) else self.shipping_method
        if not self.payment_method:
            self.payment_method = PaymentMethod.objects.filter(first_choice=True).last() if PaymentMethod.objects.filter(first_choice=True) else self.payment_method
        get_items = self.cart_items.all()
        self.value = get_items.aggregate(total=(Sum(F('final_value') * F('qty'), output_field=models.DecimalField())))['total'] if get_items else 0
        current_value = self.value
        current_value += self.payment_method.estimate_additional_cost(self.value) if self.payment_method else 0
        current_value += self.shipping_method.estimate_additional_cost(self.value) if self.shipping_method else 0
        self.final_value = current_value - self.coupon_discount
        super(Cart, self).save(*args, **kwargs)

    def tag_value(self):
        return '%s %s' % (round(self.value, 2), CURRENCY)

    def tag_final_value(self):
        return '%s %s' % (round(self.final_value, 2), CURRENCY)

    def tag_payment_cost(self):
        cost = self.payment_method.estimate_additional_cost(self.value) if self.payment_method else 0
        return '%s %s' % (round(cost, 2), CURRENCY) 

    def tag_shipping_cost(self):
        cost = self.shipping_method.estimate_additional_cost(self.value) if self.shipping_method else 0
        return '%s %s' % (round(cost,2), CURRENCY) 

    def tag_to_order(self):
        return 'Done' if self.is_complete else 'Not Done'

    @staticmethod
    def costumer_changes(request, cart):
        payment_method = request.POST.get('payment_method', cart.payment_method)
        shipping_method = request.POST.get('shipping_method', cart.shipping_method)
        add_coupon = request.POST.get('add_coupon', None)
        if isinstance(int(payment_method), int):
            cart.payment_method = PaymentMethod.objects.get(id=payment_method)
        if shipping_method:
            if isinstance(int(shipping_method), int):
                cart.shipping_method = Shipping.objects.get(id=shipping_method)
        cart.save()
        if add_coupon:
            coupons = Coupons.objects.filter(code=add_coupon)
            if coupons.exists():
                coupon = coupons.first()
                if coupon.whole_order:
                    cart.coupon.add(coupon)
                    cart.save()
                elif coupon.categories:
                    items = cart.order_items.all()
                    categories = items.values('category_site')
                    for category in coupon.categories:
                        if category in categories:
                            cart.coupon.add(coupon)
                            break
            cart.save()


class CartItemManager(models.Manager):

    def check_if_exists(self, order_related, product):
        return super(CartItemManager, self).filter(order_related=order_related,
                                                   product_related=product
                                                   )


class CartItem(models.Model):
    order_related = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product_related = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    characteristic = models.ForeignKey(SizeAttribute, blank=True, null=True, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                validators=[validate_positive_decimal,
                                            ])
    price_discount = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                         validators=[validate_positive_decimal, ]
                                         )
    final_value = models.DecimalField(default=0, decimal_places=2, max_digits=10, validators=[validate_positive_decimal,])
    my_query = CartItemManager()
    objects = models.Manager()

    def __str__(self):
        if self.characteristic:
            return f'{self.product_related.title} - {self.characteristic.title}'
        return self.product_related.title

    def save(self, *args, **kwargs):
        self.final_value = self.price_discount if self.price_discount > 0 else self.price
        super(CartItem, self).save(*args, **kwargs)
        self.order_related.save()

    @property
    def get_total_value(self):
        return self.final_value*Decimal(self.qty)

    def tag_price(self):
        return '%s %s' % (round(self.price, 2), CURRENCY)

    def tag_total_value(self):
        return '%s %s' % (round(self.get_total_value, 2), CURRENCY)

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)

    def tag_total_value(self):
        total_value = self.qty*self.final_value
        return '%s %s' % (total_value, CURRENCY)

    def update_order(self):
        items_query = CartItem.objects.filter(order_related=self.order_related)
        self.order_related.value += items_query.aggregate(total=Sum(F('qty')*F('final_value')))['total'] if items_query.exists() else 0
        self.order_related.save()

    def edit_cart_item(self, old_price):
        self.order_related.value -= old_price
        self.order_related.value += Decimal(self.get_total_price)
        self.order_related.save()

    def delete_from_order(self):
        self.order_related.value -= self.price
        self.order_related.save()
        if not self.qty == 1:
            self.qty -= 1
            self.save()
        else:
            self.delete()

    @staticmethod
    def create_cart_item(request, order, product, qty, size=None):
        product_qty = product.qty
        if size:
            qs_exists = CartItem.objects.filter(order_related=order, product_related=product, characteristic=size)
        else:
            qs_exists = CartItem.objects.filter(order_related=order, product_related=product)
        if qs_exists:
            cart_item = qs_exists.last()
            if RETAIL_TRANSCATIONS:
                cart_qty = cart_item.qty + qty
                if product_qty >= cart_qty:
                    cart_item.qty += qty
                    cart_item.save()
                else:
                    messages.warning(request, 'WE dont have enough qty.')
            else:
                cart_item.qty += qty
                cart_item.save()
            return cart_item
        else:
            if RETAIL_TRANSCATIONS:
                if qty > product_qty:
                    messages.warning(request, 'WE dont have enough qty.')
                else:
                    new_cart_item = CartItem.objects.create(order_related=order,
                                                            product_related=product,
                                                            qty=qty,
                                                            price=product.price,
                                                            price_discount=product.price_discount,
                                                            )
                    if size and new_cart_item:
                        new_cart_item.characteristic = size
                        new_cart_item.save()
                    messages.success(request, 'The product %s added in your cart' % (product.title))
                    return new_cart_item
            else:
                new_cart_item = CartItem.objects.create(order_related=order,
                                                        product_related=product,
                                                        qty=qty,
                                                        price=product.price,
                                                        price_discount=product.price_discount,
                                                        )
                if size and new_cart_item:
                    new_cart_item.characteristic = size
                    new_cart_item.save()
                messages.success(request, 'The product %s added in your cart' % (product.title))
                return new_cart_item
        

@receiver(post_delete, sender=CartItem)
def update_order_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.order_related
    get_order.save()


class CartRules(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    coupons = models.ManyToManyField(Coupons)
    payment_value = models.PositiveIntegerField(default=0)
    shipping_value = models.PositiveIntegerField(default=0)

    def estimate_shipping_value(self):
        value = self.cart.value
        shipping_method = self.cart.shipping_method
        shipping_value = 5
        if shipping_method:
            shipping_value = shipping_method.value if shipping_method.value_limit < value else 0
        return shipping_value

    def estimate_payment_type(self):
        payment_method = self.cart.payment_method
        payment_value = 2
        if payment_method:
            payment_value = 5 if payment_method == 1 and payment_method else 0
        return payment_value

    def save(self, *args, **kwargs):
        self.payment_value = self.estimate_payment_type()
        self.shipping_value = self.estimate_shipping_value()
        super(CartRules, self).save(*args, **kwargs)


class CartGiftItem(models.Model):
    cart_related = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='gifts')
    product_related = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.cart_related

    @staticmethod
    def check_cart(cart):
        if cart:
            gifts = cart.gifts.all() 
            gifts.delete()
            items = cart.cart_items.all()
            for item in items:
                can_be_gift = Gifts.objects.filter(product_related=item.product_related)
                if can_be_gift.exists:
                    for gift in can_be_gift:
                        new_gift = CartGiftItem.objects.create(product_related=gift.products_gift,
                                                            cart_related=cart,
                                                            qty=item.qty
                                                            )
        
