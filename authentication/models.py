from typing import Any, List, Optional, Tuple
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from . import manager

# Define authentication methods as type-safe tuple
AUTH_METHOD: Tuple[Tuple[str, str], ...] = (
    ("Credentials", "Credentials"),
    ("Google", "Google"),
    ("Github", "Github"),
)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that extends Django's AbstractBaseUser.
    Implements custom fields and methods for user authentication and management.
    """
    username = models.CharField(
        max_length=1000,
        unique=True,
        primary_key=True,
        db_index=True,
        help_text="Unique identifier for the user"
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        blank=True,
        null=True,
        help_text="User's email address"
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    method = models.CharField(
        max_length=50,
        default="Credentials",
        choices=AUTH_METHOD,
        help_text="Authentication method used"
    )

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # purchased_courses = models.ManyToManyField(
    #     "course.Course",
    #     blank=True,
    #     related_name='purchasers'
    # )

    image = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(
        max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(
        max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    # Explicitly disable unused fields
    groups = None
    user_permissions = None
    last_login = None

    objects = manager.UserManager()

    REQUIRED_FIELDS: List[str] = ["first_name", "last_name", "email"]
    USERNAME_FIELD: str = "username"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["first_name"]

    def __str__(self) -> str:
        return self.username
