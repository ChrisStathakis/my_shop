from django.db import models
from django.db.models import Sum, Q, F
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.conf import settings
import os, datetime
from decimal import Decimal
from tinymce.models import HTMLField

from site_settings.models import DefaultBasicModel
from frontend.models import CategorySite, Brands
from inventory_manager.models import Vendor, Category

from site_settings.constants import MEDIA_URL, CURRENCY, UNIT
from .managers import ProductManager

WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS

def product_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'product/{0}/{1}'.format(instance.product.title, filename)


def upload_location(instance, filename):
    return "%s%s" %(instance.id, filename)


def my_awesome_upload_function(instance, filename):
    """ this function has to return the location to upload the file """
    return os.path.join('/media_cdn/%s/' % instance.id, filename)


class Characteristics(DefaultBasicModel):
    title = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.title


class CharacteristicsValue(DefaultBasicModel):
    title = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.title


class ProductCharacteristics(models.Model):
    title = models.ForeignKey(Characteristics, on_delete=models.CASCADE)
    value = models.ForeignKey(CharacteristicsValue, on_delete=models.CASCADE)
    objects = models.Manager()
    
    def __str__(self):
        return f'{self.title.title} - {self.value.title}'


class Color(DefaultBasicModel):
    code_id = models.CharField(max_length=25, blank=True, verbose_name='Κωδικός Χρώματος')
    
    class Meta:
        verbose_name_plural = '5. Χρώματα'
        ordering = ['-costum_ordering', ]

    def __str__(self):
        return self.title

    def tag_active(self):
        return 'Active' if self.active else 'No Active'

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class Size(DefaultBasicModel):

    class Meta:
        verbose_name_plural = '6. Μεγέθη'
        ordering = ['costum_ordering', ]

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:edit_size', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(status=True) if active_name else queryset
        return queryset


class Product(DefaultBasicModel):
    site_active = models.BooleanField(default=True, verbose_name='Active for Site')
    wholesale_active = models.BooleanField(default=False, verbose_name="Active for WholeSale")
    is_service = models.BooleanField(default=False, verbose_name='Service')
    is_featured = models.BooleanField(default=False, verbose_name='Featured Product')
    is_offer = models.BooleanField(default=True)
    size = models.BooleanField(default=False, verbose_name='Μεγεθολόγιο')
    color = models.ForeignKey(Color, blank=True, null=True, verbose_name='Χρώμα', on_delete=models.CASCADE)
    #  warehouse data
    order_code = models.CharField(null=True, blank=True, max_length=100, verbose_name="Κωδικός Τιμολογίου")
    price_buy = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Αγοράς") # the price which you buy the product
    order_discount = models.IntegerField(default=0, verbose_name="'Εκπτωση Τιμολογίου σε %")
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    vendor = models.ForeignKey(Vendor, verbose_name="Προμηθευτής", blank=True, null=True, on_delete=models.SET_NULL)

    qty_kilo = models.DecimalField(max_digits=5, decimal_places=3, default=1, verbose_name='Βάρος/Τεμάχια ανά Συσκευασία ')
    qty = models.DecimalField(default=0, verbose_name="Απόθεμα", max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=6, null=True, blank=True, verbose_name='Κωδικός/Barcode')
    notes = models.TextField(null=True, blank=True, verbose_name='Περιγραφή')
    measure_unit = models.CharField(max_length=1, default='1', choices=UNIT, blank=True, null=True)
    safe_stock = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    objects = models.Manager()
    my_query = ProductManager()

    #site attritubes
    sku = models.CharField(max_length=150, blank=True, null=True)
    site_text = HTMLField(blank=True, null=True)
    category_site = models.ManyToManyField(CategorySite, blank=True, null=True)
    brand = models.ForeignKey(Brands, blank=True, null=True, verbose_name='Brand Name', on_delete=models.SET_NULL)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    # price sell and discount sells
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή λιανικής") #the price product have in the store
    margin = models.IntegerField(default=30, verbose_name='Margin', blank=True, null=True)
    markup = models.IntegerField(default=30, verbose_name='Markup', blank=True, null=True)
    price_internet = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Internet(No use)")
    price_b2b = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Χονδρικής") #the price product have in the website, if its 0 then website gets the price from store
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωτική Τιμή.')
    final_price = models.DecimalField(default=0, decimal_places=2, max_digits=10, blank=True)
    #size and color

    related_products = models.ManyToManyField('self', blank=True)
    different_color = models.ManyToManyField('self', blank=True)
    characteristics = models.ManyToManyField(ProductCharacteristics)

    class Meta:
        verbose_name_plural = "1. Προϊόντα"
        ordering = ['-id', ]

    def save(self, *args, **kwargs):
        if self.price:
            self.final_price = self.price_discount if self.price_discount > 0 else self.price
        self.is_offer = True if self.price_discount > 0 else False
        super(Product, self).save(*args, **kwargs)

    def update_product(self, transcation, qty):
        if transcation == 'add':
            self.qty += qty
            self.save()
        if transcation == 'remove':
            self.qty -= qty
            self.save()

    def update_qty(self):
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            pass
        else:
            items = self.related_products.all()
            self.qty = items.aggregate(Sum('qty'))['qty__sum'] if items else self.qty
            self.save()

    def __str__(self):
        return '%s %s' % (self.title, self.color) if self.color else self.title

    def get_edit_url(self):
        return reverse('dashboard:product_detail', kwargs={'pk': self.id})

    def get_absolute_url(self):
        return reverse('product_page', kwargs={'slug': self.slug})

    def tag_ware_category(self):
        return f'{self.category.title}' if self.category else 'No category selected'

    def tag_site_category(self):
        return f'{self.category_site.first()}' if self.category_site.first() else 'No category selected'

    def tag_brand(self):
        return f'{self.brand}' if self.brand else 'No brand selected'

    def tag_category(self):
        return self.category.title if self.category else 'No Category'

    def tag_vendor(self):
        return self.vendor.title if self.vendor else 'No Supplier'

    def tag_featured(self):
        return mark_safe('<td style="background-color:#a4e8a4;">Featured</td>') if self.is_featured else mark_safe('<td style="background-color:#d8a0a0;">No Featured</td>')

    def tag_active(self):
        return mark_safe('<td style="background-color:#a4e8a4;">Active</td>') if self.active and self.site_active else mark_safe('<td style="background-color:#d8a0a0;">No Active</td>')

    def tag_final_show_price(self):
        return f'{self.price_discount} {CURRENCY} from {self.price} {CURRENCY}' if self.price_discount > 0 else f'{self.price} {CURRENCY}'

    @property
    def tag_final_price(self):
        return '%s %s' % (self.final_price, CURRENCY)

    @property
    def get_final_price_buy(self):
        return self.price_buy*((100-self.order_discount)/100)
        
    @property
    def tag_final_price_buy(self):
        return '%s %s' % (self.get_final_price_buy, CURRENCY)
        
    @property
    def tag_price_buy(self):
        return '%s %s' % (self.price_buy, CURRENCY)

    def tag_price(self):
        return '%s %s' % (self.price, CURRENCY)

    def tag_remain_warehouse_price_buy(self):
        return '%s %s' % (self.price_buy*self.qty, CURRENCY)

    def tag_remain_warehouse_final_price(self):
        return '%s %s' % (self.final_price*self.qty, CURRENCY)

    def tag_qty(self):
        return '%s %s' % (self.qty, self.get_measure_unit_display())
    
    def tag_qty_td(self):
        return mark_safe('<td>%s</td>' % self.tag_qty()) if self.qty > 0 else mark_safe(f'<td style="background-color:#d8a0a0;">{self.tag_qty()}</td>')

    @property
    def image(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_primary=True).last().image
        except:
            pass

    @property
    def image_back(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_back=True).last().image
        except:
            pass

    
    @property
    def sizes(self):
        return SizeAttribute.objects.filter(product_related=self, qty__gte=1)

    def get_all_images(self):
        return ProductPhotos.objects.filter(active=True, product=self)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s%s" class="img-responsive">'%(MEDIA_URL, self.image))
        return mark_safe('<img src="%s" class="img-responsive">' % "{% static 'home/no_image.png' %}")

    def image_back_tag(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIA_URL, self.image_back))

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img src="%s%s" width="100px" height="100px">' % (MEDIA_URL, self.image))

    def image_back_tag_tiny(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">' % (MEDIA_URL, self.image))

    def show_warehouse_remain(self):
        return self.qty * self.qty_kilo

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        site_cate_name = request.GET.getlist('site_cate_name', None)
        brand_name = request.GET.getlist('brand_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        color_name = request.GET.getlist('color_name', None)
        feat_name = request.GET.get('feat_name', None)
        active_name = request.GET.get('active_name', None)
        size_name = request.GET.get('size_name', None)
        size_data_name = request.GET.get('size_data_name', None)
        discount_name = request.GET.get('discount_name')
        qty_name = request.GET.get('qty_exists_name')
        qty_up_name = request.GET.get('qty_up_name')
        qty_down_name = request.GET.get('qty_down_name')
    
        queryset = queryset.filter(active=True, site_active=True) if active_name == '1' else queryset.filter(active=False, site_active=False) if active_name == '2' else queryset  
        queryset = queryset.filter(size=True) if size_data_name else queryset
        queryset = queryset.filter(price_discount__gt=0) if discount_name else queryset
        queryset = queryset.filter(qty__gt=0) if qty_name else queryset

        queryset = queryset.filter(is_featured=True) if feat_name == '1' else queryset
        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(brand__id__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
        queryset = queryset.filter(category_site__id__in=site_cate_name) if site_cate_name else queryset
        queryset = queryset.filter(color__id__in=color_name) if color_name else queryset
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        if size_name:
            queryset = queryset.filter(size=True)
            sizes_selected = SizeAttribute.objects.filter(title__id__in=size_name, product_related__in=queryset)
            my_ids = sizes_selected.values('product_related')
            queryset = queryset.filter(id__in=my_ids)
        return queryset

    
class SizeAttributeManager(models.Manager):
    def active_for_site(self):
        return super(SizeAttributeManager, self).filter(qty__gte=0)

    def instance_queryset(self, instance):
        return self.active_for_site().filter(product_related=instance)


class SizeAttribute(models.Model):
    title = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name='Νούμερο', related_name='sizes')
    product_related = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, verbose_name='Προϊόν', related_name='product_sizes')
    qty = models.DecimalField(default=0, decimal_places=2, max_digits=6, verbose_name='Ποσότητα')
    order_discount = models.IntegerField(null=True, blank=True, default=0,verbose_name="'Εκπτωση Τιμολογίου σε %")
    price_buy = models.DecimalField(decimal_places=2,max_digits=6,default=0,verbose_name="Τιμή Αγοράς")
    my_query = SizeAttributeManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '2. Μεγεθολόγιο'
        unique_together = ['title', 'product_related']
        ordering = ['title']

    def save(self, *args, **kwargs):
        get_sizes = SizeAttribute.objects.filter(product_related=self.product_related)
        super(SizeAttribute, self).save(*args, **kwargs)
        self.product_related.qty = get_sizes.aggregate(Sum('qty'))['qty__sum'] if get_sizes else 0
        self.product_related.save()

    def __str__(self):
        return '%s - %s'%(self.product_related, self.title)

    def check_product_in_order(self):
        return str(self.product_related + '. Χρώμα : ' + self.title.title + ', Μέγεθος : ' + self.title.title)

    def delete_update_product(self):
        self.product_related.qty -= self.qty
        self.product_related.save()

    def tag_final_price(self):
        final_price = self.product_related.final_price if not self.product_related.price_buy == self.price_buy else self.price_buy
        return '%s %s' % (final_price, CURRENCY)
    tag_final_price.short_description = 'Τιμή Αγοράς'


class ProductPhotos(models.Model):
    image = models.ImageField()
    alt = models.CharField(null=True, blank=True, max_length=200, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    title = models.CharField(null=True ,blank=True, max_length=100, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, verbose_name='Αρχική Εικόνα')
    is_back = models.BooleanField(default=False, verbose_name='Δεύτερη Εικόνα')

    class Meta:
        verbose_name_plural = 'Gallery'
        ordering = ['is_primary', ]

    def __str__(self):
        return self.title

    def image_status(self):
        return 'Primary Image' if self.is_primary else 'Secondary Image' if self.is_back else 'Image'

    def image_tag(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIA_URL, self.image))
    image_tag.short_description = 'Εικονα'

    def image_tag_tiny(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIA_URL, self.image))
    image_tag_tiny.short_description = 'Εικόνα'

    def tag_status(self):
        return 'First Picture' if self.is_primary else 'Back Picture' if self.is_back else 'Picture'
    
    def tag_primary(self):
        return 'Primary' if self.is_primary else 'No Primary'

    def tag_secondary(self):
        return 'Secondary' if self.is_back else "No Back Image"


class Gifts(models.Model):
    title = models.CharField(max_length=150, unique=True)
    gift_message = models.CharField(max_length=200, unique=True)
    status = models.BooleanField(default=False)
    product_related = models.ManyToManyField(Product, related_name='product_related')
    products_gift = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title
    



