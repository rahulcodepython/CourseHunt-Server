from rest_framework import serializers
from .models import Blog


class BaseBlogPostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(
        format="%b %d %Y", read_only=True
    )  # Common field
    updated_at = serializers.DateField(
        format="%b %d %Y", read_only=True
    )  # Common field

    class Meta:
        model = Blog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ListBlogPostSerializer(BaseBlogPostSerializer):
    class Meta(BaseBlogPostSerializer.Meta):
        fields = ["id", "title", "created_at", "image"]
