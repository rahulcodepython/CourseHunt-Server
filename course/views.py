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

    @catch_exception
    def get(self, request):
        page_no = 1 if request.GET.get("page") == None else request.GET.get("page")

        if request.user.is_authenticated:
            if cache.get(f"list_all_published_courses_{request.user}_page_{page_no}"):
                response_data = cache.get(
                    f"list_all_published_courses_{request.user}_page_{page_no}"
                )
                return response.Response(
                    response_data,
                    status=status.HTTP_200_OK,
                )
        else:
            if cache.get(f"list_all_published_courses_anonymous_page_{page_no}"):
                response_data = cache.get(
                    f"list_all_published_courses_anonymous_page_{page_no}"
                )
                return response.Response(
                    response_data,
                    status=status.HTTP_200_OK,
                )

        courses = models.Course.objects.all().filter(status="published").order_by("-id")
        paginator = Paginator(courses, 2)
        page = paginator.page(page_no)
        courses = page.object_list

        response_data = {
            "count": paginator.count,
            "next": pagination_next_url_builder(page, "course/list-course/"),
        }

        if request.user.is_authenticated:
            serializer = serializers.ListCoursesSerializer(
                courses, many=True, context={"user": request.user}
            )

            response_data = {
                "results": serializer.data,
                **response_data,
            }
            cache.set(
                f"list_all_published_courses_{request.user}_page_{page_no}",
                response_data,
                timeout=60,
            )
        else:
            serializer = serializers.ListCoursesSerializer(
                courses, many=True, context={"user": None}
            )

            response_data = {
                "results": serializer.data,
                **response_data,
            }
            cache.set(
                f"list_all_published_courses_anonymous_page_{page_no}",
                response_data,
                timeout=60,
            )

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class AdminListCoursesView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        page_no = 1 if request.GET.get("page") == None else request.GET.get("page")

        if cache.get(f"list_all_courses_for_admin_page_{page_no}"):
            response_data = cache.get(f"list_all_courses_for_admin_page_{page_no}")
            return response.Response(
                response_data,
                status=status.HTTP_200_OK,
            )

        courses = models.Course.objects.all().order_by("-id")
        paginator = Paginator(courses, 2)
        page = paginator.page(page_no)
        courses = page.object_list

        serializer = serializers.ListCoursesAdminDashboardSerializer(courses, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, "course/admin-list-course/"),
        }

        cache.set(
            f"list_all_courses_for_admin_page_{page_no}", response_data, timeout=60
        )

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request):
        page_no = 1 if request.GET.get("page") == None else request.GET.get("page")

        if cache.get(f"list_all_purchased_courses_{request.user}_page_{page_no}"):
            response_data = cache.get(
                f"list_all_purchased_courses_{request.user}_page_{page_no}"
            )
            return response.Response(
                response_data,
                status=status.HTTP_200_OK,
            )

        if request.user.is_superuser:
            courses = models.Course.objects.all().order_by("-id")
        else:
            profile = Profile.objects.get(user=request.user)
            courses = profile.purchased_courses.all().order_by("-id")

        paginator = Paginator(courses, 1)
        page = paginator.page(page_no)
        courses = page.object_list

        serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, "course/purchased-courses/"),
        }

        cache.set(
            f"list_all_purchased_courses_{request.user}_page_{page_no}",
            response_data,
            timeout=60,
        )

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request, course_id):
        if cache.get(f"edit_course_{course_id}"):
            response_data = cache.get(f"edit_course_{course_id}")
            return response.Response(
                response_data,
                status=status.HTTP_200_OK,
            )

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

        if cache.get(f"edit_course_{course_id}"):
            cache.delete(f"edit_course_{course_id}")

        return Message.success("Course updated successfully")

    @catch_exception
    def delete(self, request, course_id):
        course = models.Course.objects.get(id=course_id)
        course.delete()

        if cache.get(f"edit_course_{course_id}"):
            cache.delete(f"edit_course_{course_id}")

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
        if cache.get(f"study_single_course_{course_id}"):
            response_data = cache.get(f"study_single_course_{course_id}")
            return response.Response(
                response_data,
                status=status.HTTP_200_OK,
            )

        course = models.Course.objects.get(id=course_id)

        if not request.user.is_superuser:
            profile = Profile.objects.get(user=request.user)
            if course not in profile.purchased_courses.all():
                return Message.warn("You have not purchased this course")

        serializer = serializers.StudySingleCourseSerializer(course)
        cache.set(f"study_single_course_{course_id}", serializer.data, timeout=60)

        return response.Response(serializer.data, status=status.HTTP_200_OK)


class DetailSingleCourseView(views.APIView):

    @catch_exception
    def get(self, request, course_id):
        if request.user.is_authenticated:
            if cache.get(f"detail_single_course_{course_id}_{request.user}"):
                response_data = cache.get(
                    f"detail_single_course_{course_id}_{request.user}"
                )
                return response.Response(
                    response_data,
                    status=status.HTTP_200_OK,
                )
        else:
            if cache.get(f"detail_single_course_{course_id}_anonymous"):
                response_data = cache.get(f"detail_single_course_{course_id}_anonymous")
                return response.Response(
                    response_data,
                    status=status.HTTP_200_OK,
                )

        course = models.Course.objects.get(id=course_id)

        if request.user.is_authenticated:
            serializer = serializers.DetailSingleCourseSerializer(
                course, context={"user": request.user}
            )
            cache.set(
                f"detail_single_course_{course_id}_{request.user}",
                serializer.data,
                timeout=60,
            )
        else:
            serializer = serializers.DetailSingleCourseSerializer(
                course, context={"user": None}
            )
            cache.set(
                f"detail_single_course_{course_id}_anonymous",
                serializer.data,
                timeout=60,
            )

        return response.Response(serializer.data, status=status.HTTP_200_OK)
