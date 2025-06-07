from rest_framework import serializers
from authentication.models import Instructor
from course.models import Course
from authentication.serializers import UserListSerializer


class BaseInstructorSerializer(serializers.ModelSerializer):
    """
    Base serializer for instructor models.
    """
    user = UserListSerializer()

    class Meta:
        model = Instructor
        fields = '__all__'


class InstructorDetailSerializer(BaseInstructorSerializer):
    courses = serializers.SerializerMethodField()
    """
    Serializer for retrieving instructor details.
    """
    class Meta(BaseInstructorSerializer.Meta):
        pass

    def get_courses(self, obj):
        # Lazy import to avoid circular dependency
        from course.serializers import CourseListForAllUsersSerializer

        courses = Course.objects.filter(instructor=obj)
        serialized = CourseListForAllUsersSerializer(courses, many=True)
        return serialized.data


class InstructorListSerializer(BaseInstructorSerializer):
    """
    Serializer for listing instructors.
    """
    class Meta(BaseInstructorSerializer.Meta):
        pass


class InstructorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'
