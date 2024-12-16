from rest_framework import response, status


class Message:
    def warn(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def error(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    def success(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_200_OK)

    def create(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_201_CREATED)
