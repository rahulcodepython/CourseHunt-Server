from rest_framework import views
from .decorators import catch_exception
from .message import Message
from django.db import connections
from django.db.utils import OperationalError


class Test(views.APIView):
    @catch_exception
    def get(self, request):
        try:
            # Check the default database connection
            connection = connections["default"]
            connection.cursor()  # Try to create a cursor to check the connection
            return Message.success("Database connection successful")

        except OperationalError:
            raise OperationalError("Database connection failed")
