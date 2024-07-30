from rest_framework import serializers
from . import models


class CourseEditSerializer(serializers.ModelSerializer):
    cupon_code = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = models.Course
        fields = [
            "name",
            "description",
            "price",
            "offer",
            "duration",
            "chapter",
            "overview",
            "cupon_code",
        ]


class ChapterEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chapter
        fields = ["id", "name", "duration"]


class LessonEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = ["id", "name"]


class FAQEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FAQ
        fields = "__all__"


class AdminCourseListSerializer(serializers.ModelSerializer):
    cupon_code = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = [
            "id",
            "name",
            "price",
            "chapter",
            "offer",
            "duration",
            "created_at",
            "status",
            "cupon_code",
        ]

    def get_cupon_code(self, obj):
        return obj.cupon_code.code if obj.cupon_code else None
