from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from authentication.models import Profile
from django.utils import timezone


class Message:
    def warn(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_406_NOT_ACCEPTABLE}

    def error(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_400_BAD_REQUEST}

    def success(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_200_OK}

    def create(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_201_CREATED}


class CreateCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.CreateCourseSerializer(data=request.data)

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            course = serializer.save()

            return response.Response({"id": course.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ListCoursesView(views.APIView):
    def get(self, request):
        try:
            courses = models.Course.objects.all().filter(status="published")
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            if request.user.is_authenticated:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": request.user}
                )
            else:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": None}
                )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class AdminListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            courses = models.Course.objects.all()
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesAdminDashboardSerializer(
                courses, many=True
            )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = get_object_or_404(Profile, user=request.user)
            courses = profile.purchased_courses.all()

            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def patch(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(
                course, data=request.data, partial=True
            )

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            serializer.save()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def delete(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            course.delete()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


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

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class StudySingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            profile = Profile.objects.get(user=request.user)
            course = models.Course.objects.get(id=course_id)

            if course not in profile.purchased_courses.all():
                res = Message.error("Course not purchased")
                return response.Response(res["body"], status=res["status"])

            serializer = serializers.StudySingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


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
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])
