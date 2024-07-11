from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings
import random

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "image", "email", "is_superuser")


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = list(User.REQUIRED_FIELDS) + [settings.AUTH_CONFIG['LOGIN_FIELD'], "password", "email"]

    def create(self, validated_data):
        user = super().create(validated_data)
        user.username = validated_data["username"]
        user.set_password(validated_data["password"])
        user.email = validated_data["email"]
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'image']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)