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
