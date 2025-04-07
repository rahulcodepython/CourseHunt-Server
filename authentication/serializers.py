from typing import Dict, Any, List, Type
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings

# Get the user model at module level
User: Type[Any] = get_user_model()

# Define common user fields
USER_BASE_FIELDS: List[str] = [
    "username",
    "first_name",
    "last_name",
    "image",
]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for general user data representation.
    Used for reading user information.
    """

    class Meta:
        model = User
        fields = tuple(USER_BASE_FIELDS + ["email", "is_superuser"])
        read_only_fields = ("is_superuser",)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles user creation with password hashing.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This email is already registered."
        )]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This username is already taken."
        )]
    )

    class Meta:
        model = User
        fields = list(User.REQUIRED_FIELDS) + [
            settings.AUTH_CONFIG["LOGIN_FIELD"],
            "password",
            "email",
        ]

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user instance with proper password hashing.

        Args:
            validated_data: Dictionary containing user data

        Returns:
            User: Created user instance

        Raises:
            serializers.ValidationError: If user creation fails
        """
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create user: {str(e)}")


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    Handles partial updates of user data.
    """

    class Meta:
        model = User
        fields = USER_BASE_FIELDS
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'image': {'required': False},
        }

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update user instance with validated data.

        Args:
            instance: Current user instance
            validated_data: Dictionary containing update data

        Returns:
            User: Updated user instance

        Raises:
            serializers.ValidationError: If update fails
        """
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to update user: {str(e)}")
