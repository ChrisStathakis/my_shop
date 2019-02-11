

def update_vendor(modeladmin, request, queryset):
    for order in queryset:
        items = order.order_items.all()
        for item in items:
            product = item.product
            product.vendor = order.vendor
            product.save()
            

def pay_orders(modeladmin, request, queryset):
    for order in queryset:
        order.is_paid = True
        order.save()

pay_orders.short_description = 'Πληρωμή Τιμολογίων'