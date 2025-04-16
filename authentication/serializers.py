from typing import Dict, Any, List, Type
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings

# Get the user model at module level
User: Type[Any] = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for general user data representation.
    Used for reading user information.
    """

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ("is_superuser",)

    def save(self, **kwargs: Dict[str, Any]) -> Any:
        """
        Save the user instance with the provided data.
        """
        user = super().save(**kwargs)
        password = kwargs.get("password")
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """
        Update the user instance with the provided data.
        """
        user = super().update(instance, validated_data)
        password = validated_data.get("password")
        if password:
            user.set_password(password)
            user.save()
        return user
