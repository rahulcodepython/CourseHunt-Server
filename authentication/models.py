from typing import Any, List, Optional, Tuple
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from . import manager as self_manager

# Define authentication methods as type-safe tuple
AUTH_METHOD: Tuple[Tuple[str, str], ...] = (
    ("Credentials", "Credentials"),
    ("Google", "Google"),
    ("Github", "Github"),
)

# Maximum field lengths
MAX_NAME_LENGTH: int = 1000
MAX_EMAIL_LENGTH: int = 254
TOKEN_LENGTH: int = 4


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that extends Django's AbstractBaseUser.
    Implements custom fields and methods for user authentication and management.
    """
    username = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        primary_key=True,
        db_index=True,
        help_text="Unique identifier for the user"
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        blank=True,
        null=True,
        help_text="User's email address"
    )
    first_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
    last_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
    image = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
    method = models.CharField(
        max_length=50,
        default="Credentials",
        choices=AUTH_METHOD,
        help_text="Authentication method used"
    )

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Explicitly disable unused fields
    groups = None
    user_permissions = None
    last_login = None

    objects = self_manager.UserManager()

    REQUIRED_FIELDS: List[str] = ["first_name", "last_name", "email"]
    USERNAME_FIELD: str = "username"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["first_name"]

    def __str__(self) -> str:
        return self.username

    def save(self, *args: Any, **kwargs: Any) -> 'User':
        """Save user and create associated profile if it doesn't exist."""
        try:
            super().save(*args, **kwargs)
            if not Profile.objects.filter(user=self).exists():
                Profile.objects.create(user=self)
            return self
        except Exception as e:
            raise ValueError(f"Failed to save user: {str(e)}")

    def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, dict]:
        """Delete user and associated profile."""
        try:
            Profile.objects.get(user=self).delete()
            return super().delete(*args, **kwargs)
        except Profile.DoesNotExist:
            return super().delete(*args, **kwargs)


class BaseCode(models.Model):
    """Base abstract model for all code-based models."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(default="", max_length=TOKEN_LENGTH)
    token = models.CharField(default="", max_length=TOKEN_LENGTH)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.user.username


class LoginCode(BaseCode):
    """Model for storing login verification codes."""
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login Code"
        verbose_name_plural = "Login Codes"


class ActivationCode(BaseCode):
    """Model for storing account activation codes."""
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activation Code"
        verbose_name_plural = "Activation Codes"


class ResetPasswordCode(BaseCode):
    """Model for storing password reset codes."""
    class Meta:
        verbose_name = "Reset Password Code"
        verbose_name_plural = "Reset Password Codes"


class ResetEmailCode(BaseCode):
    """Model for storing email reset codes."""
    new_email = models.EmailField(
        default="",
        max_length=MAX_EMAIL_LENGTH,
        help_text="New email address to be verified"
    )

    class Meta:
        verbose_name = "Reset Email Code"
        verbose_name_plural = "Reset Email Codes"


class Profile(models.Model):
    """User profile model storing additional user information."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    purchased_courses = models.ManyToManyField(
        "course.Course",
        blank=True,
        related_name='purchasers'
    )
    country = models.CharField(
        max_length=MAX_NAME_LENGTH, blank=True, null=True)
    city = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
    address = models.CharField(
        max_length=MAX_NAME_LENGTH, blank=True, null=True)
    phone = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self) -> str:
        return self.user.username
