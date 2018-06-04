from django.db import models


class RetailOrderManager(models.Manager):
    def all_orders_by_date_filter(self, date_start, date_end):
        return super(RetailOrderManager, self).filter(date_created__range=[date_start, date_end]).order_by('-date_created')

    def sells_orders(self, date_start, date_end):
        return self.all_orders_by_date_filter(date_start, date_end).filter(order_type__in=['r', 'e']).exclude(status__in=['5', '6'])

    def sellings_done(self):
        return super(RetailOrderManager, self).filter(status__id__in=[7,8]).exclude(order_type='b').order_by('-date_created')

    def sellings_not_done(self):
        return super(RetailOrderManager, self).exclude(status__id__in=[7,8], order_type='b')

    def eshop_orders(self):
        return super(RetailOrderManager, self).filter(order_type='e')

    def eshop_new_orders(self):
        return super(RetailOrderManager, self).filter(order_type='e', status_id=1).order_by('-id')

    def paid_orders(self):
        return super(RetailOrderManager, self).filter(is_paid=True)

    def eshop_done_orders(self, date_start, date_end):
        return super(RetailOrderManager, self).filter(order_type__in=['e','r'], status__id=7, date_created__range=[date_start, date_end])

    def eshop_orders_on_progress(self):
        return super(RetailOrderManager, self).filter(order_type='e', status__id__in=[2, 3, 4, 5])

    def eshop_orders_in_warehouse(self):
        return super(RetailOrderManager, self).filter(order_type='e', status__id__in=[1, 2, 3, 4, 5])

    def retail_orders(self, date_start=None, date_end=None):
        if date_start and date_end:
            return super(RetailOrderManager, self).filter(order_type='r', date_created__range=[date_start, date_end]).order_by('-date_created')
        return super(RetailOrderManager, self).filter(order_type='r').order_by('-date_created')


