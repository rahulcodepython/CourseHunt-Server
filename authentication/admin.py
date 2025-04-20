from typing import List
from django.contrib import admin
from . import models
from django.conf import settings
from django.contrib.auth.models import Group


admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_NAME
admin.site.index_title = settings.SITE_NAME

admin.site.unregister(Group)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model with customized display fields."""

    list_display: List[str] = [
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]
    search_fields: List[str] = ["email", "username"]
    list_filter: List[str] = ["is_active", "is_superuser"]


@admin.register(models.Instructor)
class InstructorAdmin(admin.ModelAdmin):
    """Admin interface for Instructor model with customized display fields."""

    list_display: List[str] = [
        "user"
    ]
