from rest_framework import serializers
from .models import Course, Module, Lecture, UserCourse, FAQ
from instructor.serializers import BaseInstructorSerializer
from authentication.serializers import UserListSerializer


def duration_to_parsed_time(duration):
    """
    Convert a duration in seconds to a human-readable format.
    """
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_parts = [
        f"{hours}h" if hours > 0 else "",
        f"{minutes}m" if minutes > 0 else "",
        f"{seconds}s" if seconds > 0 else ""
    ]
    return " ".join(part for part in duration_parts if part)


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'


class LectureListSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = ("title", "order", "duration", "type")

    def get_duration(self, obj):
        return duration_to_parsed_time(obj.duration)


class ModuleSerializer(serializers.ModelSerializer):
    lectures = LectureListSerializer(many=True, required=False)

    class Meta:
        model = Module
        fields = '__all__'

    def create(self, validated_data):
        lectures_data = validated_data.pop('lectures', [])
        module = Module.objects.create(**validated_data)
        for lecture_data in lectures_data:
            lecture = Lecture.objects.create(**lecture_data)
            module.lectures.add(lecture)
        return module


class ModuleListSerializer(ModuleSerializer):
    lectures = LectureListSerializer(many=True)
    total_lectures = serializers.SerializerMethodField()
    lecture_duration = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = '__all__'

    def get_total_lectures(self, obj):
        return obj.lectures.count()

    def get_lecture_duration(self, obj):
        return duration_to_parsed_time(obj.lecture_duration)


class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        exclude = ["last_completed_lecture", "completed_lectures"]
        read_only_fields = ('user', 'purchase_date')


class FAQListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('question', 'answer')


class BaseCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course


# class CourseSerializer(BaseCourseSerializer):
#     modules = ModuleSerializer(many=True, required=False)
#
#     class Meta(BaseCourseSerializer.Meta):
#         fields = '__all__'
#
#     def create(self, validated_data):
#         modules_data = validated_data.pop('modules', [])
#         course = Course.objects.create(**validated_data)
#
#         for module_data in modules_data:
#             lectures_data = module_data.pop('lectures', [])
#             module = Module.objects.create(**module_data)
#
#             for lecture_data in lectures_data:
#                 lecture = Lecture.objects.create(**lecture_data)
#                 module.lectures.add(lecture)
#
#             course.modules.add(module)
#
#         return course


class CourseListForAllUsersSerializer(BaseCourseSerializer):
    instructor = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    """
    Serializer for listing all courses for all users.
    Inherits from BaseCourseSerializer to include course details.
    """
    class Meta(BaseCourseSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'image',
            'badge',
            'price',
            'discount_price',
            'discount_percentage',
            'rating',
            'rating_count',
            'created_at',
            'instructor'
        )

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %B, %Y")

    def get_instructor(self, obj):
        return UserListSerializer(obj.instructor.user).data


class CourseDetailForAllUsersSerializer(CourseListForAllUsersSerializer):
    instructor = BaseInstructorSerializer()
    user_course = serializers.SerializerMethodField()
    modules = ModuleListSerializer(many=True)
    faq = FAQListSerializer(many=True)

    class Meta(CourseListForAllUsersSerializer.Meta):
        fields = '__all__'

    def get_user_course(self, obj):
        user = self.context['user']
        user_course = UserCourse.objects.filter(user=user, course=obj).first()

        if user_course is None:
            return False

        return True
