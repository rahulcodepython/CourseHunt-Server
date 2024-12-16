from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
from django.shortcuts import get_object_or_404
from server.decorators import catch_exception
from server.message import Message
from django.conf import settings
from django.core.cache import cache

BASE_API_URL = settings.BASE_API_URL


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
        page_no = 1 if request.GET.get("page") == None else request.GET.get("page")

        if cache.get(f"feedbacks_{page_no}"):
            feedbacks = cache.get(f"feedbacks_{page_no}")
            return response.Response(feedbacks, status=status.HTTP_200_OK)

        feedbacks = models.Feedback.objects.all().order_by("-id")
        paginator = Paginator(feedbacks, 1)
        page = paginator.page(page_no)
        feedbacks = page.object_list

        serializer = serializers.FeedbackSerializer(feedbacks, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": (
                f"{BASE_API_URL}/feedback/list/?page={page.next_page_number()}"
                if page.has_next()
                else None
            ),
        }

        cache.set(f"feedbacks_{page_no}", response_data)

        return response.Response(
            response,
            status=status.HTTP_200_OK,
        )


class DeleteFeedback(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def delete(self, request, id):
        feedback = get_object_or_404(models.Feedback, id=id)
        feedback.delete()
        return Message.success("Feedback deleted successfully.")
