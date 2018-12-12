from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'password']