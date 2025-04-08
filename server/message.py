from rest_framework import status
from rest_framework.response import Response


class Message:
    """
    A utility class for creating standardized HTTP responses with appropriate status codes.
    """

    @staticmethod
    def warn(msg: str) -> Response:
        """
        Returns a warning response with a 406 Not Acceptable status code.

        Args:
            msg (str): The warning message to include in the response.

        Returns:
            Response: A DRF Response object with the warning message and status code.
        """
        response_data: dict = {"error": msg}  # Prepare response data
        response_status: int = status.HTTP_406_NOT_ACCEPTABLE  # Set status code
        # Return response
        return Response(response_data, status=response_status)

    @staticmethod
    def error(msg: str) -> Response:
        """
        Returns an error response with a 400 Bad Request status code.

        Args:
            msg (str): The error message to include in the response.

        Returns:
            Response: A DRF Response object with the error message and status code.
        """
        response_data: dict = {"error": msg}  # Prepare response data
        response_status: int = status.HTTP_400_BAD_REQUEST  # Set status code
        # Return response
        return Response(response_data, status=response_status)

    @staticmethod
    def success(msg: str) -> Response:
        """
        Returns a success response with a 200 OK status code.

        Args:
            msg (str): The success message to include in the response.

        Returns:
            Response: A DRF Response object with the success message and status code.
        """
        response_data: dict = {"success": msg}  # Prepare response data
        response_status: int = status.HTTP_200_OK  # Set status code
        # Return response
        return Response(response_data, status=response_status)

    @staticmethod
    def create(msg: str) -> Response:
        """
        Returns a creation success response with a 201 Created status code.

        Args:
            msg (str): The success message to include in the response.

        Returns:
            Response: A DRF Response object with the success message and status code.
        """
        response_data: dict = {"success": msg}  # Prepare response data
        response_status: int = status.HTTP_201_CREATED  # Set status code
        # Return response
        return Response(response_data, status=response_status)
