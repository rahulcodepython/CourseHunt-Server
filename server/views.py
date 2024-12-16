from rest_framework import views
from .decorators import catch_exception
from .message import Message


class Test(views.APIView):
    @catch_exception
    def get(self, request):
        return Message.success("Test successful")
