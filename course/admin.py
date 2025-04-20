from django.contrib import admin
from .models import Course, Module, Lecture, UserCourse, FAQ


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_published')
    list_filter = ('is_published',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'lecture_duration')


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'video_url')


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('course', 'question', 'answer')
