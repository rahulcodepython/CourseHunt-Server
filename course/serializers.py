from rest_framework import serializers
from . import models


class BaseCourseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(format="%b %d %Y")  # Common field

    class Meta:
        model = models.Course  # Common model reference


class CreateCourseSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta): ...

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class StudySingleCourseSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
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


class DetailSingleCourseSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        exclude = [
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]


class ListCoursesDashboardSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        fields = [
            "id",
            "name",
            "created_at",
            "price",
            "offer",
            "status",
        ]


class ListCoursesSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
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


class BaseCouponSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(format="%b %d %Y")  # Common field

    class Meta:
        model = models.CuponeCode
        fields = "__all__"


class CreateCouponSerializer(serializers.ModelSerializer):
    class Meta(BaseCouponSerializer.Meta): ...

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ListCouponSerializer(BaseCouponSerializer):
    class Meta(BaseCouponSerializer.Meta): ...
