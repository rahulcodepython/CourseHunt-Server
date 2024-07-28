from django.contrib import admin
from . import models


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "duration", "chapter", "created_at")


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "duration")


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "answer")


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "question")


@admin.register(models.CuponCode)
class CuponCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "discount", "expiry", "quantity")
