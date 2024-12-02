from rest_framework import serializers
from . import models


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class StudySingleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        exclude = [
            "status",
            "short_description",
            "long_description",
            "price",
            "offer",
            "duration",
            "thumbnail",
            "created_at",
        ]


class DetailSingleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        exclude = [
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]


class ListCoursesDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = [
            "id",
            "name",
            "created_at",
            "price",
            "offer",
            "status",
        ]


class ListCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        exclude = [
            "long_description",
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Purchase
        fields = "__all__"
