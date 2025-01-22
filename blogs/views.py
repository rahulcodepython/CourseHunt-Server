from rest_framework import views, status, response, permissions
from .models import Blog, Comment
from server.decorators import catch_exception
from .serializers import (
    ListBlogPostSerializer,
    ReadBlogPostSerializer,
    CreateCommentSerializer,
    AdminListBlogPostSerializer,
    CreateBlogPostSerializer,
)
from django.core.cache import cache
from django.core.paginator import Paginator
from server.utils import pagination_next_url_builder
from server.message import Message


class ListAllBlogsView(views.APIView):

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        cache_key = f"all_blogs_{page_no}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        blogs = Blog.objects.all().order_by("-created_at")
        paginator = Paginator(blogs, 2)
        page = paginator.get_page(page_no)
        serialized = ListBlogPostSerializer(page, many=True)

        data = {
            "results": serialized.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(cache_key, data)  # Cache for 15 minutes
        return response.Response(data, status=status.HTTP_200_OK)


class AdminListAllBlogsView(views.APIView):

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 2)

        blogs = Blog.objects.all().order_by("-created_at")
        paginator = Paginator(blogs, page_size)
        page = paginator.get_page(page_no)
        serialized = AdminListBlogPostSerializer(page, many=True)

        data = {
            "results": serialized.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(data, status=status.HTTP_200_OK)


class ReadBlogView(views.APIView):

    @catch_exception
    def get(self, request, blog_id):
        cache_key = f"blogs_{blog_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        blog = Blog.objects.get(id=blog_id)
        serialized = ReadBlogPostSerializer(blog, context={"request": request})
        cache.set(cache_key, serialized.data)
        return response.Response(serialized.data, status=status.HTTP_200_OK)


class CreateCommentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request):
        serialized = CreateCommentSerializer(
            data=request.data, context={"request": request}
        )
        serialized.is_valid(raise_exception=True)
        serialized.save()
        blog = Blog.objects.get(id=request.data["blog"])
        blog.comments += 1
        blog.save()
        serialized_data = serialized.data
        serialized_data.pop("blog", None)
        serialized_data.pop("parent", None)
        cache.delete(f"blogs_{request.data['blog']}")
        return response.Response(serialized_data, status=status.HTTP_201_CREATED)


class LikeBlogView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        liked = True
        user = request.user
        if user in blog.like.all():
            blog.like.remove(user)
            blog.likes -= 1
            liked = False
        else:
            blog.like.add(user)
            blog.likes += 1
        blog.save()
        cache.delete(f"blogs_{blog_id}")
        return response.Response({"liked": liked}, status=status.HTTP_200_OK)


class CreateBlogView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request):
        serialized = CreateBlogPostSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Message.success(msg="Blog is created.")


class UpdateBlogView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        serialized = CreateBlogPostSerializer(blog)
        return response.Response(serialized.data, status=status.HTTP_200_OK)

    @catch_exception
    def patch(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        serialized = CreateBlogPostSerializer(blog, data=request.data, partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        cache.delete(f"blogs_{blog_id}")
        return Message.success(msg="Blog is updated.")

    @catch_exception
    def delete(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        cache.delete(f"blogs_{blog_id}")
        return Message.success(msg="Blog is deleted.")


class UpdateComment(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        comment.content = request.data["content"]
        comment.save()
        cache.delete(f"blogs_{comment.blog.id}")
        return response.Response(
            {"content": comment.content, "id": comment_id}, status=status.HTTP_200_OK
        )

    @catch_exception
    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        cache.delete(f"blogs_{comment.blog.id}")
        return Message.success(msg="Comment is deleted.")
