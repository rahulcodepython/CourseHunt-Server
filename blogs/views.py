from rest_framework import views, status, response
from .models import Blog, Comment
from server.decorators import catch_exception
from .serializers import ListBlogPostSerializer
from django.core.cache import cache
from django.core.paginator import Paginator
from server.utils import pagination_next_url_builder


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
