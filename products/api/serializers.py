from rest_framework import serializers
from ..models import Product
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['title', 'final_price', 'qty']


class HyperProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ['title', 'final_price', 'qty']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class MySerializer(serializers.Serializer):
    title = serializers.CharField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    qty = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        return Product.objects.create(**validated_data)
