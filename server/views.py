from typing import Any  # For type hinting
from rest_framework.views import APIView  # Import only the required class
from rest_framework.request import Request  # For type hinting request
from rest_framework.response import Response  # For type hinting response
from django.db import connections
from django.db.utils import OperationalError
from .decorators import catch_exception
from .message import Message


class Test(APIView):
    """
    APIView to test the database connection and return a success or failure message.
    """

    @catch_exception
    def get(self, request: Request) -> Response:
        """
        Handles GET requests to check the database connection.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A success or failure message based on the database connection status.
        """
        try:
            # Get the default database connection
            connection = connections["default"]

            # Attempt to create a cursor to verify the connection
            with connection.cursor() as cursor:
                pass  # Cursor creation successful, no further action needed

            # Return a success message if the connection is valid
            success_message: str = "Database connection successful"
            return Message.success(success_message)

        except OperationalError as e:
            # Handle database connection failure
            error_message: str = "Database connection failed"
            raise OperationalError(error_message) from e
