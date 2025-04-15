from rest_framework import views, status, response, permissions
from typing import Dict, Any, Optional
from django.core.paginator import Paginator, Page
from django.http import HttpRequest
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from .models import Blog, Comment
from server.decorators import catch_exception
from .serializers import (
    ListBlogPostSerializer,
    ReadBlogPostSerializer,
    CreateCommentSerializer,
    AdminListBlogPostSerializer,
    CreateBlogPostSerializer,
)
from server.utils import pagination_next_url_builder
from server.message import Message


class ListAllBlogsView(views.APIView):
    """API view for listing all blog posts with pagination and caching."""

    @catch_exception
    def get(self, request: HttpRequest) -> response.Response:
        """
        Retrieve a paginated list of all blogs.

        Args:
            request: HTTP request object containing query parameters.

        Returns:
            Response with paginated blog data.
        """
        # Extract pagination parameters from request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = 3  # Fixed page size for pagination

        # Fetch blogs from the database
        blogs: QuerySet[Blog] = Blog.objects.all().order_by("-created_at")
        paginator: Paginator = Paginator(blogs, page_size)
        page: Page = paginator.get_page(page_no)

        # Serialize the paginated data
        serialized_data = ListBlogPostSerializer(page, many=True).data

        # Prepare response data
        data: Dict[str, Any] = {
            "results": serialized_data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(data, status=status.HTTP_200_OK)


class AdminListAllBlogsView(views.APIView):
    """API view for admin to list all blog posts with pagination."""

    @catch_exception
    def get(self, request: HttpRequest) -> response.Response:
        """
        Retrieve a paginated list of all blogs for admin.

        Args:
            request: HTTP request object containing query parameters.

        Returns:
            Response with paginated blog data.
        """
        # Extract pagination parameters from request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Fetch blogs from the database
        blogs: QuerySet[Blog] = Blog.objects.all().order_by("-created_at")
        paginator: Paginator = Paginator(blogs, page_size)
        page: Page = paginator.get_page(page_no)

        # Serialize the paginated data
        serialized_data = AdminListBlogPostSerializer(page, many=True).data

        # Prepare response data
        data: Dict[str, Any] = {
            "results": serialized_data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(data, status=status.HTTP_200_OK)


class ReadBlogView(views.APIView):
    """API view for reading a single blog post."""

    @catch_exception
    def get(self, request: HttpRequest, blog_id: int) -> response.Response:
        """
        Retrieve a single blog post by its ID.

        Args:
            request: HTTP request object.
            blog_id: ID of the blog to retrieve.

        Returns:
            Response with blog data.
        """
        # Fetch the blog from the database
        blog: Blog = get_object_or_404(Blog, id=blog_id)

        # Serialize the blog data
        serialized_data = ReadBlogPostSerializer(
            blog, context={"request": request}).data

        return response.Response(serialized_data, status=status.HTTP_200_OK)


class CreateCommentView(views.APIView):
    """API view for creating a comment on a blog post."""
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request: HttpRequest) -> response.Response:
        """
        Create a new comment for a blog post.

        Args:
            request: HTTP request object containing comment data.

        Returns:
            Response with created comment data.
        """
        # Deserialize and validate the request data
        serialized = CreateCommentSerializer(
            data=request.data, context={"request": request})
        serialized.is_valid(raise_exception=True)
        serialized.save()

        # Update the blog's comment count
        blog: Blog = get_object_or_404(Blog, id=request.data["blog"])
        blog.comments += 1
        blog.save()

        # Prepare response data
        serialized_data: Dict[str, Any] = serialized.data
        serialized_data.pop("blog", None)
        serialized_data.pop("parent", None)

        return response.Response(serialized_data, status=status.HTTP_201_CREATED)


class LikeBlogView(views.APIView):
    """API view for liking or unliking a blog post."""
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request: HttpRequest, blog_id: int) -> response.Response:
        """
        Like or unlike a blog post.

        Args:
            request: HTTP request object.
            blog_id: ID of the blog to like or unlike.

        Returns:
            Response indicating the like status.
        """
        # Fetch the blog from the database
        blog: Blog = get_object_or_404(Blog, id=blog_id)
        user = request.user

        # Toggle the like status
        if user in blog.like.all():
            blog.like.remove(user)
            blog.likes -= 1
            liked: bool = False
        else:
            blog.like.add(user)
            blog.likes += 1
            liked: bool = True

        # Save the blog
        blog.save()
        return response.Response({"liked": liked}, status=status.HTTP_200_OK)


class CreateBlogView(views.APIView):
    """API view for creating a new blog post."""
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request: HttpRequest) -> response.Response:
        """
        Create a new blog post.

        Args:
            request: HTTP request object containing blog data.

        Returns:
            Response indicating success.
        """
        # Deserialize and validate the request data
        serialized = CreateBlogPostSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Message.success(msg="Blog is created.")


class UpdateBlogView(views.APIView):
    """API view for updating or deleting a blog post."""
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request: HttpRequest, blog_id: int) -> response.Response:
        """
        Retrieve a blog post for editing.

        Args:
            request: HTTP request object.
            blog_id: ID of the blog to retrieve.

        Returns:
            Response with blog data.
        """
        blog: Blog = get_object_or_404(Blog, id=blog_id)
        serialized_data = CreateBlogPostSerializer(blog).data
        return response.Response(serialized_data, status=status.HTTP_200_OK)

    @catch_exception
    def patch(self, request: HttpRequest, blog_id: int) -> response.Response:
        """
        Update a blog post.

        Args:
            request: HTTP request object containing updated data.
            blog_id: ID of the blog to update.

        Returns:
            Response indicating success.
        """
        blog: Blog = get_object_or_404(Blog, id=blog_id)
        serialized = CreateBlogPostSerializer(
            blog, data=request.data, partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()

        return Message.success(msg="Blog is updated.")

    @catch_exception
    def delete(self, request: HttpRequest, blog_id: int) -> response.Response:
        """
        Delete a blog post.

        Args:
            request: HTTP request object.
            blog_id: ID of the blog to delete.

        Returns:
            Response indicating success.
        """
        blog: Blog = get_object_or_404(Blog, id=blog_id)
        blog.delete()

        return Message.success(msg="Blog is deleted.")


class UpdateComment(views.APIView):
    """API view for updating or deleting a comment."""
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request: HttpRequest, comment_id: int) -> response.Response:
        """
        Update a comment.

        Args:
            request: HTTP request object containing updated comment data.
            comment_id: ID of the comment to update.

        Returns:
            Response with updated comment data.
        """
        comment: Comment = get_object_or_404(Comment, id=comment_id)
        comment.content = request.data["content"]
        comment.save()

        return response.Response(
            {"content": comment.content, "id": comment_id}, status=status.HTTP_200_OK
        )

    @catch_exception
    def delete(self, request: HttpRequest, comment_id: int) -> response.Response:
        """
        Delete a comment.

        Args:
            request: HTTP request object.
            comment_id: ID of the comment to delete.

        Returns:
            Response indicating success.
        """
        comment: Comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()

        return Message.success(msg="Comment is deleted.")
