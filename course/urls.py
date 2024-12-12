from django.urls import path
from . import views

urlpatterns = [
    path("create-course/", views.CreateCourseView.as_view(), name="create-course"),
    path("list-course/", views.ListCoursesView.as_view(), name="list-courses"),
    path(
        "detail-single-course/<str:course_id>/",
        views.DetailSingleCourseView.as_view(),
        name="detail-single-course",
    ),
    path(
        "admin-list-course/",
        views.AdminListCoursesView.as_view(),
        name="admin-list-courses",
    ),
    path(
        "purchased-courses/",
        views.PurchasedListCoursesView.as_view(),
        name="purchased-courses",
    ),
    path(
        "edit-course/<str:course_id>/",
        views.EditCourseView.as_view(),
        name="edit-course",
    ),
    path(
        "toggle-course-status/<str:course_id>/",
        views.ToggleCourseStatusView.as_view(),
        name="delete-course",
    ),
    path(
        "study-single-course/<str:course_id>/",
        views.StudySingleCourseView.as_view(),
        name="single-course",
    ),
]
