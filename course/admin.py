from django.contrib import admin  # Importing admin module to register models
from .models import Course  # Importing the Course model for admin registration


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Course model.
    This class customizes the admin interface for the Course model.
    """
    # Defining the fields to display in the admin list view
    list_display: tuple[str, str, str, str] = (
        "id",  # Display the ID of the course
        "name",  # Display the name of the course
        "price",  # Display the price of the course
        "duration",  # Display the duration of the course
    )
