from django.contrib.auth.models import Group
from django.contrib import admin
from . import models

admin.site.unregister(Group)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]


@admin.register(models.ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "uid", "token", "created_at"]


@admin.register(models.ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "uid", "token"]


@admin.register(models.ResetEmailCode)
class ResetEmailCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "uid", "token"]


@admin.register(models.LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "uid", "token", "created_at"]


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user"]
