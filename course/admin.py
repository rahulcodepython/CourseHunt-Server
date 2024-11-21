from django.contrib import admin
from . import models


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "duration", "created_at")


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "amount", "is_paid", "created_at")
