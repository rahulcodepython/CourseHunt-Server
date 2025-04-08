from django.contrib import admin  # Importing Django admin module
from .models import Feedback  # Importing the Feedback model

# Register your models here.


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin class for managing Feedback model in the Django admin interface.
    """

    # List of fields to display in the admin panel
    list_display: list[str] = ["user", "feedback", "rating", "created_at"]

    # Additional configurations or methods can be added here if needed
