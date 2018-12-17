from site_settings.models import PaymentMethod
from django.conf import settings

RETAIL_TRANSCATIONS, PRODUCT_ATTRITUBE_TRANSCATION = settings.RETAIL_TRANSCATIONS, \
                                                      settings.PRODUCT_ATTRITUBE_TRANSCATION


def update_warehouse(instance, transcation_type, qty):
    #  transcation_type = ['add', 'remove', 'change', 'delete']
    order = instance.order
    product = instance.title
    if not RETAIL_TRANSCATIONS:
        pass
    if transcation_type == 'REMOVE':
        if order.order_type in ['r', 'e']:
            get_total_value = instance.total_value
            get_total_cost = instance.total_cost_value
            product.qty += instance.qty
            print('remove qty', product.qty, instance.qty)
            product.save()
            if PRODUCT_ATTRITUBE_TRANSCATION and instance.size:
                instance.size.qty += instance.qty
                instance.size.save()
            if instance.order.costumer_account:
                costumer = instance.order.costumer_account
                costumer.balance -= get_total_cost
                costumer.save()
        if order.order_type in ['c', 'b']:
            get_total_value = instance.total_value
            get_total_cost = instance.total_cost_value
            product.qty += instance.qty
            product.save()
            if PRODUCT_ATTRITUBE_TRANSCATION and instance.size:
                instance.size.qty += instance.qty
                instance.size.save()
            if instance.order.costumer_account:
                costumer = instance.order.costumer_account
                costumer.balance -= get_total_cost
                costumer.save()

    if transcation_type == 'ADD':
        if order.order_type in ['r', 'e']:
            get_total_value = instance.total_value
            get_total_cost = instance.total_cost_value
            product.qty -= qty
            product.save()
            if PRODUCT_ATTRITUBE_TRANSCATION and instance.size:
                instance.size.qty -= qty
                instance.size.save()
            if instance.order.costumer_account:
                costumer = instance.order.costumer_account
                costumer.balance += get_total_cost
                costumer.save()




def payment_method_default():
    exists = PaymentMethod.objects.exists()
    return PaymentMethod.objects.first() if exists else None