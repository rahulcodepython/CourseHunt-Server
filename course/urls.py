from django.urls import path
from . import views

urlpatterns = [
    path("create-course/", views.CreateCourseView.as_view(), name="create-course"),
    path("list-course/", views.ListCoursesView.as_view(), name="list-courses"),
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
        "single-course/<str:course_id>/",
        views.SingleCourseView.as_view(),
        name="single-course",
    ),
    path(
        "detail-single-course/<str:course_id>/",
        views.DetailSingleCourseView.as_view(),
        name="detail-single-course",
    ),
    path(
        "purchase-course/<str:course_id>/",
        views.PurchaseCourseView.as_view(),
        name="purchase-course",
    ),
    path(
        "delete-course/<str:course_id>/",
        views.DeleteCourseView.as_view(),
        name="delete-course",
    ),
]
