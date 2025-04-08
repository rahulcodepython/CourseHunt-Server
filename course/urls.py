"""
This module defines URL patterns for the course app.
Each URL is mapped to a specific view for handling requests.
"""

from django.urls import path  # Importing path for URL routing
from . import views  # Importing views from the current package

# URL patterns for the course app
urlpatterns: list[path] = [
    # URL for creating a course
    path(
        "create-course/",
        views.CreateCourseView.as_view(),  # View for creating a course
        name="create-course",  # Name for reverse URL resolution
    ),
    # URL for listing all courses
    path(
        "list-course/",
        views.ListCoursesView.as_view(),  # View for listing courses
        name="list-courses",  # Name for reverse URL resolution
    ),
    # URL for viewing details of a single course
    path(
        "detail-single-course/<str:course_id>/",
        views.DetailSingleCourseView.as_view(),  # View for course details
        name="detail-single-course",  # Name for reverse URL resolution
    ),
    # URL for admin to list all courses
    path(
        "admin-list-course/",
        views.AdminListCoursesView.as_view(),  # Admin view for listing courses
        name="admin-list-courses",  # Name for reverse URL resolution
    ),
    # URL for listing purchased courses
    path(
        "purchased-courses/",
        views.PurchasedListCoursesView.as_view(),  # View for purchased courses
        name="purchased-courses",  # Name for reverse URL resolution
    ),
    # URL for editing a course
    path(
        "edit-course/<str:course_id>/",
        views.EditCourseView.as_view(),  # View for editing a course
        name="edit-course",  # Name for reverse URL resolution
    ),
    # URL for toggling the status of a course
    path(
        "toggle-course-status/<str:course_id>/",
        views.ToggleCourseStatusView.as_view(),  # View for toggling course status
        name="toggle-course-status",  # Name for reverse URL resolution
    ),
    # URL for studying a single course
    path(
        "study-single-course/<str:course_id>/",
        views.StudySingleCourseView.as_view(),  # View for studying a course
        name="study-single-course",  # Name for reverse URL resolution
    ),
]
