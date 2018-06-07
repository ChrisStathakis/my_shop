from rest_framework import serializers

from ..models import RetailOrder, RetailOrderItem


class RetailOrderSerializer(serializers.ModelSerializer):
    title = serializers.HyperlinkedIdentityField(view_name='api_retail_detail', format='html')

    class Meta:
        model = RetailOrder
        fields = ['title', 'final_value', 'order_items']


