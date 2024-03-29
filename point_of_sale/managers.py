from django.db import models
from datetime import datetime


class RetailQuerySet(models.QuerySet):

    def sells(self, date_start, date_end):
        return self.filter(order_type__in=['r', 'e'],
                           date_expired__range=[date_start, date_end]
                           )

    def today_sells(self):
        return self.sells().filter(date_expired=datetime.now())
    
    def returns(self, date_start, date_end):
        return self.filter(order_type='b',
                           date_expired__range=[date_start, date_end]
                           )

    def export_invoices(self, date_start, date_end):
        return self.filter(order_type='wr',
                           date_expired__range=[date_start, date_end]
                           )

    def sells_by_date_range(self, date_start, date_end):
        return self.sells().filter(date_expired__range=[date_start, date_end])
    
    def all_by_date_range(self, date_start, date_end):
        return self.filter(date_expired__range=[date_start, date_end])


class RetailOrderManager(models.Manager):

    def get_queryset(self):
        return RetailQuerySet(self.model, using=self._db)


    def all_orders_by_date_filter(self, date_start, date_end):
        return super(RetailOrderManager, self).filter(date_expired__range=[date_start, date_end])

    def sells_orders(self, date_start, date_end):
        return self.all_orders_by_date_filter(date_start, date_end).filter(order_type__in=['r', 'e'])

    def sellings_done(self):
        return super(RetailOrderManager, self).filter(status__id__in=[7,8]).exclude(order_type='b').order_by('-date_created')

    def sellings_not_done(self):
        return super(RetailOrderManager, self).exclude(status__id__in=[7,8], order_type='b')

    def eshop_orders(self):
        return super(RetailOrderManager, self).filter(order_type='e')

    def eshop_new_orders(self):
        return super(RetailOrderManager, self).filter(status='1')

    def eshop_sent_orders(self):
        return self.eshop_orders().filter(status__in=['5','6','7','8'])

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


class RetailOrderItemManager(models.Manager):
    def all_orders_by_date_filter(self, date_start, date_end):
        return super(RetailOrderItemManager, self).filter(order__date_created__range=[date_start, date_end])

    def selling_order_items(self, date_start, date_end):
        return super(RetailOrderItemManager, self).filter(order__order_type__in=['e', 'r'],
                                                          order__date_created__range=[date_start, date_end])

    def return_order_items(self, date_start, date_end):
        return super(RetailOrderItemManager ,self).filter(order__order_type='b',
                                                          order__date_created__range=[date_start, date_end])

