"""
Serializers for the Course app.
This module contains serializers for creating, updating, and retrieving course data.
"""

from typing import Any, Dict, Optional  # For type hints
# Import Profile model for user-related operations
from authentication.models import Profile
from rest_framework import serializers  # Import serializers from DRF
from . import models  # Import models from the current app


class BaseCourseSerializer(serializers.ModelSerializer):
    """
    Base serializer for Course model, providing common fields and configurations.
    """
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date for readability
    )

    class Meta:
        model = models.Course  # Reference to the Course


class CreateCourseSerializer(BaseCourseSerializer):
    """
    Serializer for creating and updating courses.
    """

    class Meta(BaseCourseSerializer.Meta):
        fields: str = "__all__"  # Include all fields from the Course model

    def create(self, validated_data: Dict[str, Any]) -> models.Course:
        """
        Create a new course instance.
        """
        return super().create(validated_data)

    def update(self, instance: models.Course, validated_data: Dict[str, Any]) -> models.Course:
        """
        Update an existing course instance.
        """
        return super().update(instance, validated_data)


class StudySingleCourseSerializer(BaseCourseSerializer):
    """
    Serializer for retrieving a single course for study purposes.
    Excludes fields not relevant for studying.
    """

    class Meta(BaseCourseSerializer.Meta):
        exclude: list[str] = [
            "status",
            "short_description",
            "long_description",
            "price",
            "offer",
            "duration",
            "thumbnail",
        ]


class DetailSingleCourseSerializer(BaseCourseSerializer):
    """
    Serializer for retrieving detailed information about a single course.
    Includes custom fields for enrolled status and creator details.
    """
    enrolled: serializers.SerializerMethodField = serializers.SerializerMethodField()
    created_by: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta(BaseCourseSerializer.Meta):
        exclude: list[str] = [
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]

    def get_enrolled(self, obj: models.Course) -> bool:
        """
        Check if the user is enrolled in the course.
        """
        user: Optional[Any] = self.context.get("user")  # Get user from context
        if user is None:  # If no user is provided, return False
            return False

        try:
            profile: Profile = Profile.objects.get(
                user=user)  # Get the user's profile
            return obj in profile.purchased_courses.all()  # Check if the course is purchased
        except Profile.DoesNotExist:
            return False  # Handle case where profile does not exist

    def get_created_by(self, obj: models.Course) -> str:
        """
        Get the full name of the course creator.
        """
        first_name: str = obj.created_by.first_name
        last_name: str = obj.created_by.last_name
        return f"{first_name} {last_name}"


class ListCoursesDashboardSerializer(BaseCourseSerializer):
    """
    Serializer for listing courses on the user dashboard.
    Includes only basic course details.
    """

    class Meta(BaseCourseSerializer.Meta):
        fields: list[str] = [
            "id",
            "name",
        ]


class ListCoursesAdminDashboardSerializer(BaseCourseSerializer):
    """
    Serializer for listing courses on the admin dashboard.
    Includes additional fields for administrative purposes.
    """

    class Meta(BaseCourseSerializer.Meta):
        fields: list[str] = [
            "id",
            "name",
            "created_at",
            "price",
            "offer",
            "status",
        ]


class ListCoursesSerializer(BaseCourseSerializer):
    """
    Serializer for listing courses with limited details.
    Includes custom field for enrolled status.
    """
    enrolled: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta(BaseCourseSerializer.Meta):
        exclude: list[str] = [
            "long_description",
            "status",
            "videoURL",
            "notesURL",
            "presentationURL",
            "codeURL",
            "content",
        ]

    def get_enrolled(self, obj: models.Course) -> bool:
        """
        Check if the user is enrolled in the course.
        """
        user: Optional[Any] = self.context.get("user")  # Get user from context
        if user is None:  # If no user is provided, return False
            return False

        try:
            profile: Profile = Profile.objects.get(
                user=user)  # Get the user's profile
            return obj in profile.purchased_courses.all()  # Check if the course is purchased
        except Profile.DoesNotExist:
            return False  # Handle case where profile does not exist
