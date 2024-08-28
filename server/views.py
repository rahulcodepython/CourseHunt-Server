from rest_framework import views, response


class Test(views.APIView):
    def get(self, request):
        return response.Response("Hello World")
