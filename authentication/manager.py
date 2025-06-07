from typing import Optional, Any, Dict
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager for handling user creation and superuser creation.
    Extends Django's BaseUserManager with custom user model support.
    """

    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields: Dict[str, Any]
    ) -> models.Model:
        """
        Create and save a regular user.

        Args:
            username: Unique username for the user
            email: Optional email address
            password: Optional password for the user
            **extra_fields: Additional fields for the user model

        Returns:
            User: Created user instance

        Raises:
            ValueError: If username is not provided
        """
        if not username:
            raise ValueError("Username must be provided")

        # Normalize email if provided
        normalized_email = (
            None if not email
            else self.normalize_email(email).lower()
        )

        # Create user instance
        user = self.model(
            username=username,
            email=normalized_email,
            **extra_fields
        )

        user.set_password(password)

        try:
            user.save(using=self._db)
        except Exception as e:
            raise ValueError(f"Failed to create user: {str(e)}")

        return user

    def create_superuser(
        self,
        username: str,
        password: str,
        email: str,
        **extra_fields: Dict[str, Any]
    ) -> models.Model:
        """
        Create and save a superuser.

        Args:
            username: Unique username for the superuser
            password: Password for the superuser
            email: Email address for the superuser
            **extra_fields: Additional fields for the user model

        Returns:
            User: Created superuser instance

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not username:
            raise ValueError("Username must be provided")
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError('Password is not provided')

        # Set superuser specific fields
        extra_fields.update({
            'is_active': True,
            'is_superuser': True,
        })

        # Create superuser instance
        user = self.model(
            username=username,
            email=self.normalize_email(email).lower(),
            **extra_fields
        )

        user.set_password(password)

        try:
            user.save(using=self._db)
        except Exception as e:
            raise ValueError(f"Failed to create superuser: {str(e)}")

        return user
