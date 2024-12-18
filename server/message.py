from rest_framework import status
from rest_framework.response import Response


class Message:
    def warn(msg: str) -> Response:
        return Response({"error": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def error(msg: str) -> Response:
        return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    def success(msg: str) -> Response:
        return Response({"success": msg}, status=status.HTTP_200_OK)

    def create(msg: str) -> Response:
        return Response({"success": msg}, status=status.HTTP_201_CREATED)
