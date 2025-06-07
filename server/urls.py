"""
This module defines the URL routing for the Django server application.
It includes routes for various app modules and handles static file serving.
"""

from django.contrib import admin  # Import admin module for admin site URLs
from django.urls import path, include  # Import path and include for URL routing
# Import static for serving static files
from django.conf.urls.static import static
# Import settings for accessing project configurations
from django.conf import settings
from . import views  # Import views for handling requests

# Define the base API path based on the environment
base_api_path: str = "" if settings.DEVELOPMENT else "api/v1/"

# Define URL patterns for the application
urlpatterns: list = [
    # Admin site URL
    # Route for Django admin panel
    path(f"{base_api_path}admin/", admin.site.urls),

    # Test view route
    path(f"{base_api_path}", views.Test.as_view()),  # Route for the Test view

    # Authentication module routes
    # Include authentication app URLs
    path(f"{base_api_path}auth/", include("authentication.urls")),

    # # Include course app URLs
    path(f"{base_api_path}course/", include("course.urls")),

    path(f"{base_api_path}instructor/", include("instructor.urls")),
]
