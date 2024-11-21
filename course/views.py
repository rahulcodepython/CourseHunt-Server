from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import os


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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            courses = models.Course.objects.all().filter(status="published")
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesSerializer(courses, many=True)

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

            serializer = serializers.ListCoursesSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            courses = user.profile.purchased_courses.all()
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

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


class SingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class DetailSingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.DetailSingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchaseCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            user = request.user

            user.profile.purchased_courses.add(course)
            user.profile.save()

            return response.Response({"id": course_id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class DeleteCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            course.delete()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])
