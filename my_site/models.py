from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

from site_settings.models import DefaultBasicModel
from site_settings.models import Country
from site_settings.constants import MEDIA_URL, CURRENCY


def validate_positive_decimal(value):
    if value < 0:
        return ValidationError('This number is negative!')
    return value


def category_site_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'category_site/{0}/{1}'.format(instance.title, filename)


class CategorySiteManager(models.Manager):
    def main_page_show(self):
        return super(CategorySiteManager, self).filter(status='a', parent__isnull=True)


class CategorySite(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=120)
    image = models.ImageField(blank=True, null=True, upload_to=category_site_directory_path, help_text='610*410')
    content = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now=True)
    meta_description = models.CharField(max_length=300, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    show_on_menu = models.BooleanField(default=False, verbose_name='Active on Navbar')
    my_query = CategorySiteManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '3. Κατηγορίες Site'
        unique_together = (('slug', 'parent',))
        ordering = ['-order', ]

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def image_tag(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="400px" height="400px" />'%(MEDIAURL, self.image))

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="100px" height="100px" />'%(MEDIAURL, self.image))
    image_tag.short_description = 'Είκονα'

    def get_edit_url(self):
        return reverse('dashboard:category_detail', kwargs={'pk': self.id})

    def get_absolute_url(self):
        return reverse('dashboard:categories')

    def absolute_url_site(self):
        pass

    def get_childrens(self):
        childrens = CategorySite.objects.filter(parent=self)
        return childrens
    
    @staticmethod
    def filter_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class Brands(models.Model):
    active = models.BooleanField(default=True, verbose_name='Ενεργοποίηση')
    title = models.CharField(max_length=120, verbose_name='Ονομασία Brand')
    image = models.ImageField(blank=True, upload_to='brands/', verbose_name='Εικόνα')
    order_by = models.IntegerField(default=1,verbose_name='Σειρά Προτεριότητας')
    meta_description =models.CharField(max_length=255, blank=True)
    width = models.IntegerField(default=240)
    height = models.IntegerField(default=240)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    class Meta:
        verbose_name_plural = '4. Brands'
        ordering = ['-title']

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img scr="%s/%s" width="400px" height="400px" />'%(MEDIA_URL, self.image))

    def image_tag_tiny(self):
        return mark_safe('<img scr="%s/%s" width="100px" height="100px" />'%(MEDIA_URL, self.image))
    image_tag.short_description = 'Είκονα'

    def get_absolute_url(self):
        return reverse('brand', kwargs={'slug': self.slug})

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class ShippingManager(models.Manager):

    def active_and_site(self):
        return super(ShippingManager, self).filter(active=True, for_site=True)
        

class Shipping(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)
    cost = models.DecimalField(max_digits=6, default=0, decimal_places=2, validators=[validate_positive_decimal, ])
    active_minimum_cost = models.DecimalField(default=40, max_digits=6, decimal_places=2,
                                              validators=[validate_positive_decimal, ])
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    ordering_by = models.IntegerField(default=1)

    class Meta:
        ordering = ['-ordering_by', ]

    def __str__(self):
        return self.title

    def estimate_cost(self, price):
        return self.cost if price < self.active_minimum_cost and self.active_cost else 0

    def tag_active_cost(self):
        return f'{self.cost} {CURRENCY}'

    def tag_active_minimum_cost(self):
        return f'{self.active_minimum_cost} {CURRENCY}'

    def tag_active(self):
        return 'Active' if self.active else 'No Active'
