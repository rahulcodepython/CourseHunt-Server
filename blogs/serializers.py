from rest_framework import serializers
from .models import Blog, Comment


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


class CreateBlogPostSerializer(BaseBlogPostSerializer):
    class Meta(BaseBlogPostSerializer.Meta):
        fields = ["id", "title", "content", "image"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return super().create(validated_data)


class ListBlogPostSerializer(BaseBlogPostSerializer):
    class Meta(BaseBlogPostSerializer.Meta):
        fields = ["id", "title", "created_at", "image"]


class AdminListBlogPostSerializer(BaseBlogPostSerializer):
    class Meta(BaseBlogPostSerializer.Meta):
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "likes",
            "read",
            "comments",
        ]


class ReadBlogPostSerializer(BaseBlogPostSerializer):
    comment = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta(BaseBlogPostSerializer.Meta):
        fields = "__all__"

    def get_comment(self, obj):
        comments = Comment.objects.filter(blog=obj, parent=None)
        return ListCommentSerializer(comments, many=True).data

    def get_liked(self, obj):
        user = self.context.get("request").user
        return user in obj.like.all()


class BaseCommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(
        format="%b %d %Y", read_only=True
    )  # Common field

    class Meta:
        model = Comment


class ListCommentSerializer(BaseCommentSerializer):
    children = serializers.SerializerMethodField()

    class Meta(BaseCommentSerializer.Meta):
        exclude = ["blog", "parent"]

    def get_children(self, obj):
        children = Comment.objects.filter(parent=obj)
        return ListCommentSerializer(children, many=True).data


class CreateCommentSerializer(BaseCommentSerializer):
    user = serializers.StringRelatedField()
    children = serializers.SerializerMethodField()

    class Meta(BaseCommentSerializer.Meta):
        fields = "__all__"
        # read_only_fields = ["blog", "parent"]

    def get_children(self, obj):
        return []

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)
