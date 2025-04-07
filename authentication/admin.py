from typing import List
from django.contrib import admin
from . import models

# Constants for admin display fields
USER_DISPLAY_FIELDS: List[str] = [
    "email",
    "first_name",
    "last_name",
    "username",
    "is_active",
    "is_superuser",
]

CODE_BASE_FIELDS: List[str] = ["user", "uid", "token"]
CODE_WITH_TIMESTAMP: List[str] = CODE_BASE_FIELDS + ["created_at"]


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model with customized display fields."""

    list_display: List[str] = USER_DISPLAY_FIELDS
    search_fields: List[str] = ["email", "username"]
    list_filter: List[str] = ["is_active", "is_superuser"]
    ordering: List[str] = ["-date_joined"]


@admin.register(models.ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    """Admin interface for ActivationCode model with tracking capabilities."""

    list_display: List[str] = CODE_WITH_TIMESTAMP
    search_fields: List[str] = ["user__email", "uid"]
    list_filter: List[str] = ["created_at"]
    ordering: List[str] = ["-created_at"]


@admin.register(models.ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    """Admin interface for ResetPasswordCode model."""

    list_display: List[str] = CODE_BASE_FIELDS
    search_fields: List[str] = ["user__email", "uid"]


@admin.register(models.ResetEmailCode)
class ResetEmailCodeAdmin(admin.ModelAdmin):
    """Admin interface for ResetEmailCode model."""

    list_display: List[str] = CODE_BASE_FIELDS
    search_fields: List[str] = ["user__email", "uid"]


@admin.register(models.LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    """Admin interface for LoginCode model with timestamp tracking."""

    list_display: List[str] = CODE_WITH_TIMESTAMP
    search_fields: List[str] = ["user__email", "uid"]
    list_filter: List[str] = ["created_at"]
    ordering: List[str] = ["-created_at"]


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for User Profile model."""

    list_display: List[str] = ["user"]
    search_fields: List[str] = ["user__email", "user__username"]
