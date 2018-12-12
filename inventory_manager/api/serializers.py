from rest_framework.serializers import ModelSerializer
from inventory_manager.models import OrderItem, Order


class WarehouseOrderSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'date_expired', 'title',
                  'vendor', 'tag_vendor',
                  'order_type', 'get_order_type_display',
                  'total_taxes', 'tag_value', 'tag_final_value',
                  'tag_paid_value',
                  ]


class WarehouseOrderItemListSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['order', 'tag_order', 'product', 'tag_product', 'unit', 'taxes', 'tag_final_value']