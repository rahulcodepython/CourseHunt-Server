from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from . import serializers, models
from authentication.models import Profile
from server.decorators import catch_exception
from server.message import Message
from server.utils import pagination_next_url_builder


class CreateCourseView(views.APIView):
    """
    API view to create a new course. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request: views.Request) -> response.Response:
        """
        Handle POST request to create a course.
        """
        serializer = serializers.CreateCourseSerializer(data=request.data)

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()
        return Message.create("Course created successfully")


class ListCoursesView(views.APIView):
    """
    API view to list all published courses with pagination.
    """
    permission_classes = [permissions.AllowAny]

    @catch_exception
    def get(self, request: views.Request) -> response.Response:
        """
        Handle GET request to list published courses.
        """
        page_no: int = int(request.GET.get("page", 1))

        # Fetch and paginate courses
        courses = models.Course.objects.filter(
            status="published").order_by("-id")
        paginator = Paginator(courses, 3)
        page = paginator.get_page(page_no)

        # Serialize data
        serializer = serializers.ListCoursesSerializer(
            page,
            many=True,
            context={
                "user": request.user if request.user.is_authenticated else None},
        )

        # Prepare response data
        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(response_data, status=status.HTTP_200_OK)


class AdminListCoursesView(views.APIView):
    """
    API view to list all courses for admin users with pagination.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request: views.Request) -> response.Response:
        """
        Handle GET request to list all courses for admin.
        """
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Fetch and paginate courses
        courses = models.Course.objects.order_by("-id")
        paginator = Paginator(courses, page_size)
        page = paginator.get_page(page_no)

        # Serialize data
        serializer = serializers.ListCoursesAdminDashboardSerializer(
            page, many=True)

        # Prepare response data
        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(response_data, status=status.HTTP_200_OK)


class PurchasedListCoursesView(views.APIView):
    """
    API view to list all purchased courses for authenticated users.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request: views.Request) -> response.Response:
        """
        Handle GET request to list purchased courses.
        """
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 1))

        # Fetch purchased courses
        if request.user.is_superuser:
            courses = models.Course.objects.order_by("-id")
        else:
            profile = get_object_or_404(Profile, user=request.user)
            courses = profile.purchased_courses.order_by("-id")

        # Paginate courses
        paginator = Paginator(courses, page_size)
        page = paginator.get_page(page_no)

        # Serialize data
        serializer = serializers.ListCoursesDashboardSerializer(
            page, many=True)

        # Prepare response data
        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(response_data, status=status.HTTP_200_OK)


class EditCourseView(views.APIView):
    """
    API view to edit, retrieve, or delete a course. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle GET request to retrieve course details.
        """
        # Fetch course and serialize data
        course = get_object_or_404(models.Course, id=course_id)
        serializer = serializers.CreateCourseSerializer(course)

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @catch_exception
    def patch(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle PATCH request to update course details.
        """
        course = get_object_or_404(models.Course, id=course_id)
        serializer = serializers.CreateCourseSerializer(
            course, data=request.data, partial=True
        )

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        return Message.success("Course updated successfully")

    @catch_exception
    def delete(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle DELETE request to remove a course.
        """
        course = get_object_or_404(models.Course, id=course_id)
        course.delete()

        return Message.success("Course deleted successfully")


class ToggleCourseStatusView(views.APIView):
    """
    API view to toggle the status of a course between draft and published.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle POST request to toggle course status.
        """
        course = get_object_or_404(models.Course, id=course_id)

        # Toggle status
        course.status = "published" if course.status == "draft" else "draft"
        course.save()

        return Message.success("Course status updated successfully")


class StudySingleCourseView(views.APIView):
    """
    API view to retrieve details of a single course for study purposes.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle GET request to retrieve course details for study.
        """
        # Fetch course
        course = get_object_or_404(models.Course, id=course_id)

        # Check if the user has purchased the course
        if not request.user.is_superuser:
            profile = get_object_or_404(Profile, user=request.user)
            if course not in profile.purchased_courses.all():
                return Message.warn("You have not purchased this course")

        # Serialize data
        serializer = serializers.StudySingleCourseSerializer(course)

        return response.Response(serializer.data, status=status.HTTP_200_OK)


class DetailSingleCourseView(views.APIView):
    """
    API view to retrieve detailed information about a single course.
    """

    @catch_exception
    def get(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle GET request to retrieve detailed course information.
        """
        # Fetch course and serialize data
        course = get_object_or_404(models.Course, id=course_id)
        serializer = serializers.DetailSingleCourseSerializer(
            course,
            context={
                "user": request.user if request.user.is_authenticated else None},
        )

        return response.Response(serializer.data, status=status.HTTP_200_OK)
