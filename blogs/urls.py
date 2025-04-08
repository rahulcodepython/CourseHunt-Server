"""
This module defines URL patterns for the blog application.
Each URL is mapped to a specific view for handling requests.
"""

from django.urls import path  # Importing path for defining URL patterns
from . import views  # Importing views from the current package

# Define URL patterns for the blog application
urlpatterns: list[path] = [
    # URL for listing all blogs
    path(
        "list/",
        views.ListAllBlogsView.as_view(),  # View for listing all blogs
        name="list_all_blogs"  # Adding a name for reverse URL resolution
    ),

    # URL for listing all blogs for admin
    path(
        "list-admin/",
        views.AdminListAllBlogsView.as_view(),  # View for admin-specific blog listing
        name="admin_list_all_blogs"
    ),

    # URL for reading a specific blog by its ID
    path(
        "read/<str:blog_id>/",
        views.ReadBlogView.as_view(),  # View for reading a blog
        name="read_blog"
    ),

    # URL for creating a comment on a blog
    path(
        "create-comment/",
        views.CreateCommentView.as_view(),  # View for creating a comment
        name="create_comment"
    ),

    # URL for liking a specific blog by its ID
    path(
        "like-blog/<str:blog_id>/",
        views.LikeBlogView.as_view(),  # View for liking a blog
        name="like_blog"
    ),

    # URL for creating a new blog
    path(
        "create/",
        views.CreateBlogView.as_view(),  # View for creating a blog
        name="create_blog"
    ),

    # URL for updating a specific blog by its ID
    path(
        "update/<str:blog_id>/",
        views.UpdateBlogView.as_view(),  # View for updating a blog
        name="update_blog"
    ),

    # URL for editing a specific comment by its ID
    path(
        "edit-comment/<str:comment_id>/",
        views.UpdateComment.as_view(),  # View for updating a comment
        name="edit_comment"
    ),
]
