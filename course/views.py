from http.client import responses

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from .models import Course, UserCourse, Lecture
from .serializers import (
    # CourseSerializer,
    UserCourseSerializer,
    # PurchaseCourseSerializer,
    # CompleteLectureSerializer,
    CourseListForAllUsersSerializer, CourseDetailForAllUsersSerializer
)
from authentication.models import User

USER = User.objects.get(username="rahul")


class CourseListForAllUsers(generics.ListAPIView):
    # get request
    permission_classes = [permissions.AllowAny]
    serializer_class = CourseListForAllUsersSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):
        return Course.objects.filter(is_published=True)


class CourseDetailForAllUsers(generics.RetrieveAPIView):
    # get request
    serializer_class = CourseDetailForAllUsersSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):
        return Course.objects.filter(is_published=True)

#
# class CourseList(generics.ListAPIView):
#     # get request
#     permission_classes = [permissions.AllowAny]
#     serializer_class = CourseSerializer
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['user'] = USER
#         # context['user'] = self.request.user
#         return context
#
#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return Course.objects.all()
#         return Course.objects.filter(is_published=True)
#
#
# class CourseDetail(generics.RetrieveAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [permissions.AllowAny]
#     # get request
#
#
# class CourseCreate(generics.CreateAPIView):
#     permission_classes = [permissions.AllowAny]
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     # post request
#
#
# class CourseUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [permissions.AllowAny]
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     # patch, delete request
#
#
# class PurchaseCourse(generics.CreateAPIView):
#     permission_classes = [permissions.AllowAny]
#     serializer_class = PurchaseCourseSerializer
#
#     def create(self, request, *args, **kwargs):
#         print(request.data)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         print(serializer.data['course_id'])
#         course = Course.objects.get(id=serializer.data['course_id'])
#         print(course)
#         user = User.objects.get(username="rahul")
#         customer, created = UserCourse.objects.get_or_create(id=f"{user.username}-c-{course.id}", user=user, course=course)
#
#         if created:
#             return Response({"status": "success"}, status=status.HTTP_201_CREATED)
#
#         return Response({"status": "purchased"}, status=status.HTTP_200_OK)
#
#         # post request
#         # {
#         #     "course_id": 1
#         # }
#
# class UserCoursesList(generics.ListAPIView):
#     permission_classes = [permissions.AllowAny]
#     serializer_class = UserCourseSerializer
#
#     def get_queryset(self):
#         user = User.objects.get(username="rahul")
#         return UserCourse.objects.filter(user=user)
#
#
# class CompleteLecture(generics.UpdateAPIView):
#     permission_classes = [permissions.AllowAny]
#     serializer_class = CompleteLectureSerializer
#
#     def update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         lecture = Lecture.objects.get(id=serializer.data['lecture_id'])
#         user_course = UserCourse.objects.get(
#             user=request.user,
#             course__modules__lectures=lecture
#         )
#         user_course.completed_lectures.add(lecture)
#         user_course.last_lecture = lecture
#         user_course.save()
#
#         return Response({"status": "lecture completed"})


# The structure of data required to create or edit a course along with module and lecture and also it is the general structure for rending a course
# {
#     "id": "2",
#     "modules": [
#         {
#             "id": "c-2-m-1",
#             "lectures": [
#                 {
#                     "id": "c-2-m-1-l-1",
#                     "title": "What is js ?",
#                     "order": 1,
#                     "video_url": "https://jfdskf.kjfkdsc.google.com",
#                     "pdf_url": "https://jfdskf.kjfkdsc.google.com",
#                     "document_url": "https://jfdskf.kjfkdsc.google.com",
#                     "text_content": "fsfds"
#                 },
#                 {
#                     "id": "c-2-m-1-l-2",
#                     "title": "What is venv.",
#                     "order": 2,
#                     "video_url": "https://jfdskf.kjfkdsc.google.com",
#                     "pdf_url": "https://jfdskf.kjfkdsc.google.com",
#                     "document_url": "https://jfdskf.kjfkdsc.google.com",
#                     "text_content": "fjskfjdksf"
#                 }
#             ],
#             "title": "js Basics",
#             "order": 1,
#             "lecture_duration": 500
#         },
#         {
#             "id": "c-2-m-2",
#             "lectures": [
#                 {
#                     "id": "c-2-m-2-l-1",
#                     "title": "React Woking.",
#                     "order": 3,
#                     "video_url": "https://jfdskf.kjfkdsc.google.com",
#                     "pdf_url": "https://jfdskf.kjfkdsc.google.com",
#                     "document_url": "https://jfdskf.kjfkdsc.google.com",
#                     "text_content": "content."
#                 },
#                 {
#                     "id": "c-2-m-2-l-2",
#                     "title": "How React works",
#                     "order": 4,
#                     "video_url": "https://jfdskf.kjfkdsc.google.com",
#                     "pdf_url": "https://jfdskf.kjfkdsc.google.com",
#                     "document_url": "https://jfdskf.kjfkdsc.google.com",
#                     "text_content": "This is the content."
#                 }
#             ],
#             "title": "React Basics",
#             "order": 2,
#             "lecture_duration": 100
#         }
#     ],
#     "instructor": "rahul",
#     "title": "React",
#     "description": "This is a short description",
#     "content": "This is a content",
#     "price": "1000.00",
#     "is_published": false,
#     "created_at": "2025-04-16T15:56:16.121325+05:30"
# }
