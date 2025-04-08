from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator, Page
from django.shortcuts import get_object_or_404
from . import serializers, models
from server.decorators import catch_exception
from server.message import Message
from server.utils import pagination_next_url_builder


class CreateFeedback(views.APIView):
    """
    API view to handle the creation of feedback.
    Only authenticated users can create feedback.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Handle POST request to create feedback.
        Validates and saves the feedback data.
        """
        # Serialize the incoming data with context
        serializer: serializers.FeedbackSerializer = serializers.FeedbackSerializer(
            data=request.data, context={"request": request}
        )
        # Validate the serialized data
        serializer.is_valid(raise_exception=True)
        # Save the feedback instance
        serializer.save()

        # Return success message
        return Message.success("Your feedback has been recorded.")


class ListFeedback(views.APIView):
    """
    API view to list all feedbacks.
    Only admin users can access this view.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request) -> response.Response:
        """
        Handle GET request to list feedbacks with pagination.
        """
        # Extract pagination parameters from the request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Query all feedbacks ordered by descending ID
        feedbacks = models.Feedback.objects.all().order_by("-id")

        # Apply pagination
        paginator: Paginator = Paginator(feedbacks, page_size)
        try:
            page: Page = paginator.page(page_no)
        except Exception as e:
            # Handle invalid page number gracefully
            return response.Response(
                {"error": f"Invalid page number: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize the paginated feedbacks
        serializer: serializers.FeedbackSerializer = serializers.FeedbackSerializer(
            page, many=True)

        # Build the response data
        response_data: dict = {
            "results": serializer.data,  # Serialized feedback data
            "count": paginator.count,  # Total number of feedbacks
            # Next page URL
            "next": pagination_next_url_builder(page, request.path),
        }

        # Return the paginated feedbacks
        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class DeleteFeedback(views.APIView):
    """
    API view to delete a specific feedback.
    Only admin users can delete feedback.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def delete(self, request, id: int) -> response.Response:
        """
        Handle DELETE request to remove a feedback by ID.
        """
        # Fetch the feedback object or return 404 if not found
        feedback: models.Feedback = get_object_or_404(models.Feedback, id=id)

        # Delete the feedback instance
        feedback.delete()

        # Return success message
        return Message.success("Feedback deleted successfully.")
