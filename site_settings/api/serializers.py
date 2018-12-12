from rest_framework import serializers

from ..models import Shipping, PaymentMethod


class ShippingListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_shipping_detail', read_only=True)

    class Meta:
        model = Shipping
        fields = ['id', 'active', 'title',
                  'additional_cost', 'tag_additional_cost',
                  'limit_value', 'tag_limit_value',
                  'country', 'first_choice',
                  'url'
                  ]


class ShippingDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipping
        fields = ['id', 'active', 'title',
                  'additional_cost', 'tag_additional_cost',
                  'limit_value', 'tag_limit_value',
                  'country', 'first_choice',
                  ]


class PaymentMethodListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_payment_method_detail', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = ['id', 'title', 'active', 'site_active', 'first_choice',
                  'additional_cost', 'limit_value', 'tag_additional_cost', 'tag_limit_value',
                  'url'
                  ]


class PaymentMethodDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = ['id', 'title', 'active', 'site_active', 'first_choice',
                  'additional_cost', 'limit_value', 'tag_additional_cost', 'tag_limit_value',
                ]