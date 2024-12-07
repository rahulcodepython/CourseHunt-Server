from rest_framework import serializers
from . import models
from authentication.models import Profile


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
        ]


class DetailSingleCourseSerializer(BaseCourseSerializer):
    enrolled = serializers.SerializerMethodField()

    class Meta(BaseCourseSerializer.Meta):
        exclude = [
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]

    def get_enrolled(self, obj):
        user = self.context.get("user")

        if user.is_anonymous:
            return False

        profile = Profile.objects.get(user=user)
        return obj in profile.purchased_courses.all()


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
    enrolled = serializers.SerializerMethodField()

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

    def get_enrolled(self, obj):
        user = self.context.get("user")

        if user.is_anonymous:
            return False

        profile = Profile.objects.get(user=user)
        return obj in profile.purchased_courses.all()


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
