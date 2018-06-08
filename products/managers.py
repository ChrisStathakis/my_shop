from django.db import models


class ProductSiteQuerySet(models.query.QuerySet):

    def active_for_site(self):
        return self.filter(active=True, site_active=True)

    def featured(self):
        return self.active_for_site().filter(is_featured=True)

    def category_queryset(self, cate):
        return self.active_for_site().filter(category_site__in=cate)


class ProductManager(models.Manager):

    def active(self):
        return super(ProductManager, self).filter(active=True)

    def active_for_site(self):
        return self.active().filter(site_active=True)

    def active_with_qty(self):
        return self.active_for_site().filter(qty__gte=0)

    def get_site_queryset(self):
        return ProductSiteQuerySet(self.model, using=self._db)

    
