from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models

# Create your views here.


class CreateFeedback(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.FeedbackSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class ListFeedback(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            feedbacks = models.Feedback.objects.all()
            serializer = serializers.FeedbackSerializer(feedbacks, many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
