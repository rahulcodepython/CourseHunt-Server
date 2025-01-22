from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
from authentication.models import Profile
from server.decorators import catch_exception
from server.message import Message
from django.core.cache import cache
from server.utils import pagination_next_url_builder


class CreateCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request):
        serializer = serializers.CreateCourseSerializer(data=request.data)

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        return Message.create("Course created successfully")


class ListCoursesView(views.APIView):

    def get_cache_key(self, request, page_no):
        if request.user.is_authenticated:
            return f"list_all_published_courses_{request.user}_page_{page_no}"
        return f"list_all_published_courses_anonymous_page_{page_no}"

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)

        cached_data = cache.get(self.get_cache_key(request, page_no))
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        courses = models.Course.objects.all().filter(status="published").order_by("-id")
        paginator = Paginator(courses, 2)
        page = paginator.page(page_no)

        serializer = serializers.ListCoursesSerializer(
            page,
            many=True,
            context={"user": request.user if request.user.is_authenticated else None},
        )

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(self.get_cache_key(request, page_no), response_data, timeout=60)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class AdminListCoursesView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 2)

        courses = models.Course.objects.all().order_by("-id")
        paginator = Paginator(courses, page_size)
        page = paginator.page(page_no)

        serializer = serializers.ListCoursesAdminDashboardSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 1)

        cache_key = f"list_all_purchased_courses_{request.user}_page_{page_no}_page_size_{page_size}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        if request.user.is_superuser:
            courses = models.Course.objects.all().order_by("-id")
        else:
            profile = Profile.objects.get(user=request.user)
            courses = profile.purchased_courses.all().order_by("-id")

        paginator = Paginator(courses, page_size)
        page = paginator.page(page_no)

        serializer = serializers.ListCoursesDashboardSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(cache_key, response_data, timeout=60)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_cache_key(self, course_id):
        return f"edit_course_{course_id}"

    @catch_exception
    def get(self, request, course_id):

        cached_data = cache.get(f"edit_course_{course_id}")
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        course = models.Course.objects.get(id=course_id)
        serializer = serializers.CreateCourseSerializer(course)

        cache.set(f"edit_course_{course_id}", serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @catch_exception
    def patch(self, request, course_id):
        course = models.Course.objects.get(id=course_id)
        serializer = serializers.CreateCourseSerializer(
            course, data=request.data, partial=True
        )

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        if cache.get(self.get_cache_key(course_id)):
            cache.delete(self.get_cache_key(course_id))

        return Message.success("Course updated successfully")

    @catch_exception
    def delete(self, request, course_id):
        course = models.Course.objects.get(id=course_id)
        course.delete()

        if cache.get(self.get_cache_key(course_id)):
            cache.delete(self.get_cache_key(course_id))

        return Message.success("Course deleted successfully")


class ToggleCourseStatusView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request, course_id):
        course = models.Course.objects.get(id=course_id)

        if course.status == "draft":
            course.status = "published"
        else:
            course.status = "draft"

        course.save()

        return Message.success("Course status updated successfully")


class StudySingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request, course_id):
        cache_key = f"study_single_course_{course_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        course = models.Course.objects.get(id=course_id)

        if not request.user.is_superuser:
            profile = Profile.objects.get(user=request.user)

            if course not in profile.purchased_courses.all():
                return Message.warn("You have not purchased this course")

        serializer = serializers.StudySingleCourseSerializer(course)

        cache.set(cache_key, serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)


class DetailSingleCourseView(views.APIView):

    def get_cache_key(self, course_id, request):
        if request.user.is_authenticated:
            return f"detail_single_course_{course_id}_{request.user}"
        return f"detail_single_course_{course_id}_anonymous"

    @catch_exception
    def get(self, request, course_id):
        cached_data = cache.get(self.get_cache_key(course_id, request))
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        course = models.Course.objects.get(id=course_id)

        serializer = serializers.DetailSingleCourseSerializer(
            course,
            context={"user": request.user if request.user.is_authenticated else None},
        )

        cache.set(self.get_cache_key(course_id, request), serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)
