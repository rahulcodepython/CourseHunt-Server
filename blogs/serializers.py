"""
Serializers for Blog and Comment models.
This module contains serializers for creating, listing, and reading blog posts and comments.
"""

from typing import Any, List  # For type annotations
from rest_framework import serializers
from .models import Blog, Comment


class BaseBlogPostSerializer(serializers.ModelSerializer):
    """
    Base serializer for Blog model, providing common fields and configurations.
    """
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date for readability
    )
    updated_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date for readability
    )

    class Meta:
        model = Blog
        fields = "__all__"  # Include all fields from the Blog model
        # Fields that cannot be modified
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateBlogPostSerializer(BaseBlogPostSerializer):
    """
    Serializer for creating a new blog post.
    """
    class Meta(BaseBlogPostSerializer.Meta):
        # Fields required for creating a blog
        fields = ["id", "title", "content", "image"]
        read_only_fields = ["id"]  # ID is read-only

    def create(self, validated_data: dict) -> Blog:
        """
        Create a new blog post with validated data.
        """
        return super().create(validated_data)


class ListBlogPostSerializer(BaseBlogPostSerializer):
    """
    Serializer for listing blog posts with limited fields.
    """
    class Meta(BaseBlogPostSerializer.Meta):
        # Fields to display in the list view
        fields = ["id", "title", "created_at", "image"]


class AdminListBlogPostSerializer(BaseBlogPostSerializer):
    """
    Serializer for admin to list blog posts with additional fields.
    """
    class Meta(BaseBlogPostSerializer.Meta):
        fields = [
            "id", "title", "created_at", "updated_at", "likes", "read", "comments"
        ]  # Include admin-specific fields


class ReadBlogPostSerializer(BaseBlogPostSerializer):
    """
    Serializer for reading a single blog post with additional details.
    """
    comment: serializers.SerializerMethodField = serializers.SerializerMethodField()
    liked: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta(BaseBlogPostSerializer.Meta):
        fields = "__all__"  # Include all fields for detailed view

    def get_comment(self, obj: Blog) -> List[dict]:
        """
        Get top-level comments for the blog post.
        """
        comments = Comment.objects.filter(
            blog=obj, parent=None)  # Fetch top-level comments
        # Serialize comments
        return ListCommentSerializer(comments, many=True).data

    def get_liked(self, obj: Blog) -> bool:
        """
        Check if the current user has liked the blog post.
        """
        user = self.context.get(
            "request").user  # Get the current user from the request context
        return user in obj.like.all()  # Check if the user is in the list of likes


class BaseCommentSerializer(serializers.ModelSerializer):
    """
    Base serializer for Comment model, providing common fields and configurations.
    """
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date for readability
    )

    class Meta:
        model = Comment
        fields = "__all__"  # Include all fields from the Comment model


class ListCommentSerializer(BaseCommentSerializer):
    """
    Serializer for listing comments with nested children.
    """
    children: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta(BaseCommentSerializer.Meta):
        # Exclude blog and parent fields from the output
        exclude = ["blog", "parent"]

    def get_children(self, obj: Comment) -> List[dict]:
        """
        Get child comments for a given comment.
        """
        children = Comment.objects.filter(parent=obj)  # Fetch child comments
        # Serialize child comments
        return ListCommentSerializer(children, many=True).data


class CreateCommentSerializer(BaseCommentSerializer):
    """
    Serializer for creating a new comment.
    """
    user: serializers.StringRelatedField = serializers.StringRelatedField()
    children: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta(BaseCommentSerializer.Meta):
        fields = "__all__"  # Include all fields for creating a comment

    def get_children(self, obj: Comment) -> List[Any]:
        """
        Return an empty list for children (no nested children on creation).
        """
        return []

    def create(self, validated_data: dict) -> Comment:
        """
        Create a new comment with the current user as the author.
        """
        request = self.context.get(
            "request")  # Get the request object from the context
        # Set the user as the current logged-in user
        validated_data["user"] = request.user
        return super().create(validated_data)
