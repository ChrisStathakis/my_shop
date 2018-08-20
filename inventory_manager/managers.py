from django.db import models


class WarehouseOrderQuerySet(models.QuerySet):

    def vendor_orders(self):
        return self.filter(order_type__in=[])