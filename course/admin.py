from django.contrib import admin
from . import models


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "duration",
    )


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "user",
        "amount",
        "is_paid",
    )


@admin.register(models.CuponeCode)
class CuponeCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount",
        "expiry",
        "quantity",
        "is_unlimited",
        "is_active",
    )
