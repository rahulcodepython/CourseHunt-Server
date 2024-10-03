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
            course = models.Course.objects.create(created_at=request.data["created_at"])

            new_chapter = models.Chapter.objects.create(course=course)
            new_chapter.save()
            course.chapters.append(new_chapter.id)

            course.save()

            return response.Response({"id": course.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, id):
        try:
            course = models.Course.objects.get(id=id)
            serialized = serializers.CourseEditSerializer(course)

            return response.Response(serialized.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def post(self, request, id):
        try:
            course = models.Course.objects.get(id=id)

            chapters_already_exists = len(course.chapters)
            new_chapters = request.data["chapter"]
            required_new_chapters = new_chapters - chapters_already_exists

            for i in range(required_new_chapters):
                new_chapter = models.Chapter.objects.create(course=course)
                new_chapter.save()
                course.chapters.append(new_chapter.id)

            course.save()

            serialized = serializers.CourseEditSerializer(
                course, data=request.data, partial=True
            )

            if not serialized.is_valid():
                print(serialized.errors)
                res = Message.error(serialized.errors)
                return response.Response(res["body"], status=res["status"])

            serialized.save()

            res = Message.create("Course is updated!")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditChapterView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, id):
        try:
            course = models.Course.objects.get(id=id)

            chapter_list = []

            for chapter in course.chapters:
                chapter = models.Chapter.objects.get(id=chapter)
                chapter_serialized = serializers.ChapterEditSerializer(chapter)

                lessons = []

                for lesson in chapter.lessons:
                    lesson = models.Lesson.objects.get(id=lesson)
                    lesson_serialized = serializers.LessonEditSerializer(lesson)
                    lessons.append(lesson_serialized.data)

                chapter_list.append({**chapter_serialized.data, "lessons": lessons})

            return response.Response({"data": chapter_list}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def post(self, request, id):
        try:
            course = models.Course.objects.get(id=id)

            for i in request.data:
                if i["id"] in course.chapters:
                    chapter = models.Chapter.objects.get(id=i["id"])
                    chapter.name = i["name"]
                    chapter.duration = i["duration"]

                    for j in i["lessons"]:
                        if "id" in j and j["id"] in chapter.lessons:
                            lesson = models.Lesson.objects.get(id=j["id"])
                            lesson.name = j["name"]
                            lesson.save()
                        else:
                            lesson = models.Lesson.objects.create(
                                name=j["name"], chapter=chapter, course=course
                            )
                            lesson.save()
                            chapter.lessons.append(lesson.id)

                    chapter.save()

            res = Message.create("Chapter is updated!")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditFAQView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, id):
        try:
            course = models.Course.objects.get(id=id)
            faq_list = []

            for faq in course.faq.all():
                faq = models.FAQ.objects.get(id=faq)
                faq_serialized = serializers.FAQEditSerializer(faq)
                faq_list.append(faq_serialized.data)

            return response.Response({"data": faq_list}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def post(self, request, id):
        try:
            course = models.Course.objects.get(id=id)

            for i in request.data["faq"]:
                if i["id"] == None:
                    faq = models.FAQ.objects.create(
                        question=i["question"], answer=i["answer"]
                    )
                    faq.save()
                    course.faq.add(faq)
                else:
                    faq = models.FAQ.objects.get(id=i["id"])
                    faq.question = i["question"]
                    faq.answer = i["answer"]
                    faq.save()

            course.save()

            res = Message.create("FAQ is updated!")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PublishCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, id):
        try:
            course = models.Course.objects.get(id=id)
            course.status = "draft" if course.status == "published" else "published"
            course.save()

            return response.Response(
                {"message": "Course is updated.", "status": course.status},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class AdminCourseList(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            page = request.GET.get("page")
            page = 1 if page is None else page

            limit = request.GET.get("limit")
            limit = 5 if limit is None else limit

            courses = models.Course.objects.all()
            serialized = serializers.AdminCourseListSerializer(courses, many=True)

            paginator = Paginator(serialized.data, limit)
            paginated = paginator.page(page)

            url = f"{os.environ.get('BASE_API_URL')}/course/admin-courses/"

            return response.Response(
                {
                    "count": paginator.count,
                    "next": (
                        f"{url}?page={paginated.next_page_number()}"
                        if paginated.has_next()
                        else None
                    ),
                    "previous": (
                        f"{url}?page={paginated.previous_page_number()}"
                        if paginated.has_previous()
                        else None
                    ),
                    "results": serialized.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])
