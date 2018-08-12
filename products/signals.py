from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Product
from frontend.models import CategorySite
from .models import SizeAttribute
import slugify


@receiver(post_save, sender=Product)
def create_product_slug(sender, instance, **kwargs):
    if not instance.slug:
        new_slug = slugify.slugify(instance.title)
        qs_exists = Product.objects.filter(slug=new_slug)
        if qs_exists.exists():
            new_slug = f'{new_slug}-{instance.id}'
        instance.slug = new_slug
        instance.save()

    
@receiver(post_save, sender=CategorySite)
def create_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        new_slug = slugify.slugify(instance.title)
        qs_exists = Product.objects.filter(slug=new_slug)
        if qs_exists.exists():
            new_slug = f'{new_slug}-{instance.id}'
        instance.slug = new_slug
        instance.save()


@receiver(post_delete, sender=SizeAttribute)
def delete_size_attribute(sender, instance, **kwargs):
    product = instance.product_related
    product.qty -= instance.qty
    product.save()