from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import F,Sum
from django.dispatch import receiver
from django.db.models.signals import post_save

from site_settings.models import Country
from site_settings.constants import CURRENCY, ADDRESS_TYPES
from carts.models import Cart


class CostumerAccountManager(models.Manager):

    def eshop_costumer(self):
        return super(CostumerAccountManager, self).filter(is_eshop=True)


class CostumerAccount(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(blank=True, null=True, max_length=150, verbose_name='First Name')
    last_name = models.CharField(blank=True, null=True, max_length=150, verbose_name='Last Name')
    #  shipping_information
    shipping_address_1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='Shipping Address')
    shipping_city = models.CharField(max_length=50, blank=True, null=True, verbose_name='City')
    shipping_zip_code = models.IntegerField(blank=True, null=True, verbose_name='Postal')
    #  billing information
    billing_name = models.CharField(max_length=100, blank=True, null=True)
    billing_address = models.CharField(max_length=100, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_zip_code = models.IntegerField(blank= True, null=True, )
    #  personal stuff
    phone = models.CharField(max_length=10, blank=True, verbose_name="Phone")
    phone1 = models.CharField(max_length=10, blank=True, verbose_name="Τηλέφωνο")
    cellphone = models.CharField(max_length=10, blank=True, verbose_name='Cell Phone')
    fax = models.CharField(max_length=10, blank=True, verbose_name="Fax")
    #  if costumer is not Retail
    is_retail = models.BooleanField(default=True)
    is_eshop = models.BooleanField(default=True)
    afm = models.CharField(max_length=9, blank=True, verbose_name="ΑΦΜ")
    DOY = models.CharField(max_length=100, blank=True, null=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Balance')
    my_query = CostumerAccountManager()
    objects = models.Manager()

    def full_name(self):
        return '%s  %s'%(self.user.first_name, self.user.last_name)

    def __str__(self):
        return self.user.username if self.user else self.first_name

    def template_tag_balance(self):
        return '%s %s' % ('{0:2f}'.format(round(self.balance, 2)),CURRENCY)

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def tag_phones(self):
        return f'{self.phone} - {self.phone1}'

    def tag_full_address(self):
        return f'{self.shipping_address_1} - {self.shipping_city}'

    def tag_first_name(self):
        return f'{self.first_name}' if len(self.first_name)>1 else None

    def tag_last_name(self):
        return f'{self.last_name}' if len(self.last_name)>1 else None

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

    def update_fields(self, form):
        self.first_name = form.cleaned_data.get('first_name', self.first_name)
        self.last_name = form.cleaned_data.get('last_name', self.last_name)
        self.shipping_address_1 = form.cleaned_data.get('address', self.shipping_address_1)
        self.shipping_city = form.cleaned_data.get('city', self.shipping_city)
        self.shipping_zip_code = form.cleaned_data.get('zip_code', self.shipping_zip_code)
        self.cellphone = form.cleaned_data.get('cellphone', self.cellphone)
        self.phone = form.cleaned_data.get('phone', self.phone)
        self.save()


@receiver(post_save, sender=User)
def create_profile(sender, instance, *args, **kwargs):
    get_profile, created = CostumerAccount.objects.get_or_create(user=instance)


class BillingProfile(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    cellphone = models.CharField(max_length=10)
    phone = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    costumer_submit = models.BooleanField(default=True, verbose_name='Are you sure?')

    def __str__(self):
        if self.cart:
            return f'{self.cart.id}'
        return f'{self.first_name, self.last_name}'


def cart_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        BillingProfile.objects.get_or_create(cart=instance)


post_save.connect(cart_created_receiver, sender=Cart)


# will be removed
class GuestEmail(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class Address(models.Model):
    billing_profile = models.OneToOneField(BillingProfile, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    postal_code = models.CharField(max_length=5)

    def __str__(self):
        if self.billing_profile.cart:
            return f'{self.billing_profile.cart.id}'
        return f'{self.billing_profile}'


def billing_profile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        Address.objects.get_or_create(billing_profile=instance)