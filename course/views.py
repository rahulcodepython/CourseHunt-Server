from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from django.core.cache import cache
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
    API view to list all published courses with pagination and caching.
    """

    def get_cache_key(self, request: views.Request, page_no: int) -> str:
        """
        Generate a cache key based on user authentication and page number.
        """
        user_key = f"{request.user}" if request.user.is_authenticated else "anonymous"
        return f"list_all_published_courses_{user_key}_page_{page_no}"

    @catch_exception
    def get(self, request: views.Request) -> response.Response:
        """
        Handle GET request to list published courses.
        """
        page_no: int = int(request.GET.get("page", 1))

        # Check cache for existing data
        cache_key: str = self.get_cache_key(request, page_no)
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch and paginate courses
        courses = models.Course.objects.filter(
            status="published").order_by("-id")
        paginator = Paginator(courses, 2)
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

        # Cache the response
        cache.set(cache_key, response_data, timeout=60)

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

        # Generate cache key
        cache_key: str = f"list_all_purchased_courses_{request.user}_page_{page_no}_page_size_{page_size}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

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

        # Cache the response
        cache.set(cache_key, response_data, timeout=60)

        return response.Response(response_data, status=status.HTTP_200_OK)


class EditCourseView(views.APIView):
    """
    API view to edit, retrieve, or delete a course. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def get_cache_key(self, course_id: int) -> str:
        """
        Generate a cache key for a specific course.
        """
        return f"edit_course_{course_id}"

    @catch_exception
    def get(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle GET request to retrieve course details.
        """
        cache_key: str = self.get_cache_key(course_id)
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch course and serialize data
        course = get_object_or_404(models.Course, id=course_id)
        serializer = serializers.CreateCourseSerializer(course)

        # Cache the response
        cache.set(cache_key, serializer.data, timeout=60)

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

        # Clear cache for the updated course
        cache_key: str = self.get_cache_key(course_id)
        cache.delete(cache_key)

        return Message.success("Course updated successfully")

    @catch_exception
    def delete(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle DELETE request to remove a course.
        """
        course = get_object_or_404(models.Course, id=course_id)
        course.delete()

        # Clear cache for the deleted course
        cache_key: str = self.get_cache_key(course_id)
        cache.delete(cache_key)

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
        cache_key: str = f"study_single_course_{course_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch course
        course = get_object_or_404(models.Course, id=course_id)

        # Check if the user has purchased the course
        if not request.user.is_superuser:
            profile = get_object_or_404(Profile, user=request.user)
            if course not in profile.purchased_courses.all():
                return Message.warn("You have not purchased this course")

        # Serialize data
        serializer = serializers.StudySingleCourseSerializer(course)

        # Cache the response
        cache.set(cache_key, serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)


class DetailSingleCourseView(views.APIView):
    """
    API view to retrieve detailed information about a single course.
    """

    def get_cache_key(self, course_id: int, request: views.Request) -> str:
        """
        Generate a cache key for a specific course based on user authentication.
        """
        user_key = f"{request.user}" if request.user.is_authenticated else "anonymous"
        return f"detail_single_course_{course_id}_{user_key}"

    @catch_exception
    def get(self, request: views.Request, course_id: int) -> response.Response:
        """
        Handle GET request to retrieve detailed course information.
        """
        cache_key: str = self.get_cache_key(course_id, request)
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch course and serialize data
        course = get_object_or_404(models.Course, id=course_id)
        serializer = serializers.DetailSingleCourseSerializer(
            course,
            context={
                "user": request.user if request.user.is_authenticated else None},
        )

        # Cache the response
        cache.set(cache_key, serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)
