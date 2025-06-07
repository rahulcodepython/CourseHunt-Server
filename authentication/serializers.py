from typing import Dict, Any
from rest_framework import serializers
from authentication.models import User

# Get the user model at module level


class UserCreateSerializer(serializers.ModelSerializer):
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


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users.
    Used for reading user information.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'image', 'is_active', 'is_superuser')
