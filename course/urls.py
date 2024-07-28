from django.urls import path
from . import views

urlpatterns = [
    path("create-course/", views.CreateCourseView.as_view(), name="create_course"),
    path("edit-course/<str:id>/", views.EditCourseView.as_view(), name="edit_course"),
    path(
        "edit-chapter/<str:id>/", views.EditChapterView.as_view(), name="edit_chapter"
    ),
    path("edit-faq/<str:id>/", views.EditFAQView.as_view(), name="edit_chapter"),
    # path("courses/", views.CourseList.as_view(), name="course_list"),
]
