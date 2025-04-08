from django.urls import path  # Import path for defining URL patterns
from . import views  # Import views from the current package

# Define URL patterns for the feedback app
urlpatterns: list[path] = [
    # URL for creating feedback
    path("create/", views.CreateFeedback.as_view()),
    path("list/", views.ListFeedback.as_view()),  # URL for listing feedback
    # URL for deleting feedback by ID
    path("delete/<str:id>/", views.DeleteFeedback.as_view()),
]
