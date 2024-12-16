from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
from django.shortcuts import get_object_or_404
from authentication.models import Profile
import os

BASE_API_URL = os.getenv("BASE_API_URL")


class Message:
    def warn(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def error(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    def success(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_200_OK)

    def create(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_201_CREATED)


class CreateCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.CreateCourseSerializer(data=request.data)

            if not serializer.is_valid():
                return Message.error(serializer.errors)

            serializer.save()

            return Message.create("Course created successfully")

        except Exception as e:
            return Message.error(str(e))


class ListCoursesView(views.APIView):
    def get(self, request):
        try:
            courses = models.Course.objects.all().filter(status="published")
            paginator = Paginator(courses, 2)
            page_no = 1 if request.GET.get("page") == None else request.GET.get("page")
            page = paginator.page(page_no)
            courses = page.object_list

            if request.user.is_authenticated:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": request.user}
                )
            else:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": None}
                )

            return response.Response(
                {
                    "results": serializer.data,
                    "count": paginator.count,
                    "next": (
                        f"{BASE_API_URL}/course/list-course/?page={page.next_page_number()}"
                        if page.has_next()
                        else None
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(str(e))


class AdminListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            page_no = 1 if request.GET.get("page") == None else request.GET.get("page")
            courses = models.Course.objects.all().order_by("-id")
            paginator = Paginator(courses, 2)
            page = paginator.page(page_no)
            courses = page.object_list

            serializer = serializers.ListCoursesAdminDashboardSerializer(
                courses, many=True
            )

            return response.Response(
                {
                    "results": serializer.data,
                    "count": paginator.count,
                    "next": (
                        f"{BASE_API_URL}/course/admin-list-course/?page={page.next_page_number()}"
                        if page.has_next()
                        else None
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(str(e))


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            if request.user.is_superuser:
                courses = models.Course.objects.all()
            else:
                profile = Profile.objects.get(user=request.user)
                courses = profile.purchased_courses.all()

            paginator = Paginator(courses, 1)
            page_no = 1 if request.GET.get("page") == None else request.GET.get("page")
            page = paginator.page(page_no)
            courses = page.object_list

            serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

            return response.Response(
                {
                    "results": serializer.data,
                    "count": paginator.count,
                    "next": (
                        f"{BASE_API_URL}/course/purchased-courses/?page={page.next_page_number()}"
                        if page.has_next()
                        else None
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(str(e))


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))

    def patch(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(
                course, data=request.data, partial=True
            )

            if not serializer.is_valid():
                return Message.error(serializer.errors)

            serializer.save()

            return Message.success("Course updated successfully")

        except Exception as e:
            return Message.error(str(e))

    def delete(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            course.delete()

            return Message.success("Course deleted successfully")

        except Exception as e:
            return Message.error(str(e))


class ToggleCourseStatusView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)

            if course.status == "draft":
                course.status = "published"
            else:
                course.status = "draft"

            course.save()

            return Message.success("Course status updated successfully")

        except Exception as e:
            return Message.error(str(e))


class StudySingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)

            if not request.user.is_superuser:
                profile = Profile.objects.get(user=request.user)
                if course not in profile.purchased_courses.all():
                    return Message.warn("You have not purchased this course")

            serializer = serializers.StudySingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))


class DetailSingleCourseView(views.APIView):
    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)

            if request.user.is_authenticated:
                serializer = serializers.DetailSingleCourseSerializer(
                    course, context={"user": request.user}
                )
            else:
                serializer = serializers.DetailSingleCourseSerializer(
                    course, context={"user": None}
                )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))
