from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Product
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