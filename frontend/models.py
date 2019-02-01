from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.db import models
from site_settings.models import DefaultBasicModel
from site_settings.constants import MEDIA_URL, CURRENCY
from mptt.models import MPTTModel, TreeForeignKey


def validate_size(value):
    if value.file.size > 0.4*1024*1024:
        raise ValidationError('This file is bigger than 0.7mb!')


def upload_location(instance, filename):
    return 'first_page/%s/%s' % (instance.title, filename)


def upload_banner(instance, filename):
    return 'banner/%s/%s' % (instance.title, filename)


def validate_positive_decimal(value):
    if value < 0:
        return ValidationError('This number is negative!')
    return value


def category_site_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'category_site/{0}/{1}'.format(instance.title, filename)


class CategorySiteManager(models.Manager):
    def main_page_show(self):
        return super(CategorySiteManager, self).filter(active=True, parent__isnull=True)

    def navbar(self):
        return super(CategorySiteManager, self).filter(active=True, show_on_menu=True)


class CategorySite(MPTTModel):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=120)
    image = models.ImageField(blank=True, null=True, upload_to=category_site_directory_path, help_text='610*410')
    content = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now=True)
    meta_description = models.CharField(max_length=300, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
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
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def image_tag(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="400px" height="400px" />'%(MEDIA_URL, self.image))

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="100px" height="100px" />'%(MEDIA_URL, self.image))
    image_tag.short_description = 'Είκονα'

    def tag_active(self):
        return 'Is Active' if self.active else 'No active'

    def tag_show_on_menu(self):
        return 'Show' if self.show_on_menu else 'No Show'

    def get_edit_url(self):
        return reverse('dashboard:category_detail', kwargs={'pk': self.id})

    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

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
    meta_description = models.CharField(max_length=255, blank=True)
    width = models.IntegerField(default=240)
    height = models.IntegerField(default=240)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    class Meta:
        verbose_name_plural = '4. Brands'
        ordering = ['title']

    def __str__(self):
        return self.title

    def tag_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="400px" height="400px" />')

    def image_tag_tiny(self):
        return mark_safe('<img scr="%s/%s" width="100px" height="100px" />'%(MEDIA_URL, self.image))
    tag_image.short_description = 'Είκονα'

    def tag_active(self):
        return 'Active' if self.active else 'No active'

    def get_absolute_url(self):
        return reverse('brand', kwargs={'slug': self.slug})

    @staticmethod
    def filters_data(queryset, request):
        search_name = request.GET.get('search_name', None)
        active_name = request.GET.getlist('active_name', None)
        brand_name = request.GET.getlist('brand_name', None)
        queryset = queryset.filter(id__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class FirstPage(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    image = models.ImageField(upload_to=upload_location, validators=[validate_size, ])
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.CharField(max_length=160)

    def __str__(self):
        return self.title

    @staticmethod
    def active_first_page():
        return FirstPage.objects.filter(active=True).first() if FirstPage.objects.filter(active=True) else None


class Banner(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=upload_banner, validators=[validate_size, ])
    href = models.URLField(blank=True, null=True)
    new_window = models.BooleanField(default=False)
    big_banner = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def tag_active(self):
        return 'Active' if self.active else 'No Active'

     