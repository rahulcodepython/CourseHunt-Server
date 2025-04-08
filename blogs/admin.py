from django.contrib import admin  # Importing Django admin module
from .models import Blog, Comment  # Importing Blog and Comment models


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Blog model.
    Displays specific fields in the admin list view.
    """
    # Fields to display in the admin list view
    list_display: list[str] = ["id", "title", "likes", "read"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.
    Displays specific fields in the admin list view.
    """
    # Fields to display in the admin list view
    list_display: list[str] = ["id", "blog", "parent", "content"]
