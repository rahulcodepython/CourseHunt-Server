from typing import Any  # For type hinting
from rest_framework.views import APIView  # Import only the required class
from rest_framework.request import Request  # For type hinting request
from rest_framework.response import Response  # For type hinting response
from django.db import connections
from django.db.utils import OperationalError
from .decorators import catch_exception
from .message import Message
# For allowing any user to access the view
from rest_framework.permissions import AllowAny


class Test(APIView):
    """
    APIView to test the database connection and return a success or failure message.
    """
    permission_classes = [AllowAny]  # No authentication required for this view

    @catch_exception
    def get(self, request: Request) -> Response:
        """
        Handles GET requests to check the database connection.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A success or failure message based on the database connection status.
        """
        return Message.success("Welcome to the API")
