from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
from django.shortcuts import get_object_or_404
from server.decorators import catch_exception
from server.message import Message
from django.conf import settings
from django.core.cache import cache
from server.utils import pagination_next_url_builder


class CreateFeedback(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request):
        serializer = serializers.FeedbackSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Message.success("Your feedback is been recorded.")


class ListFeedback(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)

        cache_key = f"feedbacks_{page_no}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        feedbacks = models.Feedback.objects.all().order_by("-id")
        paginator = Paginator(feedbacks, 1)
        page = paginator.page(page_no)

        serializer = serializers.FeedbackSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(cache_key, response_data, timeout=60)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class DeleteFeedback(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def delete(self, request, id):
        feedback = get_object_or_404(models.Feedback, id=id)
        feedback.delete()
        return Message.success("Feedback deleted successfully.")
