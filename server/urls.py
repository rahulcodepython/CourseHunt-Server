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
import os  # Import os for environment variable handling
from . import views  # Import views for handling requests

# Get the current environment (default to "local" if not set)
environment: str = os.getenv("ENVIRONMENT", "local")

# Define the base API path based on the environment
base_api_path: str = "api" if environment == "production" else ""

# Define URL patterns for the application
urlpatterns: list = [
    # Admin site URL
    # Route for Django admin panel
    path(f"{base_api_path}/admin/", admin.site.urls),

    # Test view route
    path(f"{base_api_path}/", views.Test.as_view()),  # Route for the Test view

    # Authentication module routes
    # Include authentication app URLs
    path(f"{base_api_path}/auth/", include("authentication.urls")),

    # Course module routes
    # Include course app URLs
    path(f"{base_api_path}/course/", include("course.urls")),

    # Feedback module routes
    # Include feedback app URLs
    path(f"{base_api_path}/feedback/", include("feedback.urls")),

    # Transactions module routes
    # Include transactions app URLs
    path(f"{base_api_path}/transactions/", include("transactions.urls")),

    # Blogs module routes
    # Include blogs app URLs
    path(f"{base_api_path}/blogs/", include("blogs.urls")),
]

# Add static file serving routes (only in development mode)
if settings.DEBUG:  # Ensure static files are served only in DEBUG mode
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
