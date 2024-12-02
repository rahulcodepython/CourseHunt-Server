from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import razorpay
from django.conf import settings
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY)
)


class Message:
    def warn(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_406_NOT_ACCEPTABLE}

    def error(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_400_BAD_REQUEST}

    def success(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_200_OK}

    def create(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_201_CREATED}


class CreateCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.CreateCourseSerializer(data=request.data)

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            course = serializer.save()

            return response.Response({"id": course.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            courses = models.Course.objects.all().filter(status="published")
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class AdminListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            courses = models.Course.objects.all()
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            courses = user.profile.purchased_courses.all()
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(
                course, data=request.data, partial=True
            )

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            serializer.save()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class StudySingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.StudySingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class DetailSingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.DetailSingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchaseCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            user = request.user

            user.profile.purchased_courses.add(course)
            user.profile.save()

            return response.Response({"id": course_id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class DeleteCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            course.delete()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class InitiatePayment(views.APIView):
    def get(self, request, course_id):
        course = get_object_or_404(models.Course, id=course_id)
        user = request.user
        amount = int(course.price * 100)  # Razorpay amount is in paisa

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(
            {"amount": amount, "currency": "INR", "payment_capture": "1"}
        )

        # Create an Order in our DB
        models.Purchase.objects.create(
            course=course,
            user=user,
            amount=course.price,
            razorpay_order_id=razorpay_order["id"],
        )

        return response.Response(
            {
                "order_id": razorpay_order["id"],
                "amount": amount,
                "currency": "INR",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyPayment(views.APIView):
    def post(self, request):
        data = request.data
        purchase = get_object_or_404(
            models.Purchase, razorpay_order_id=data["razorpay_order_id"]
        )

        # Verify Razorpay Signature
        try:
            razorpay_client.utility.verify_payment_signature(data)
            purchase.is_paid = True
            purchase.razorpay_payment_id = data["razorpay_payment_id"]
            purchase.razorpay_signature = data["razorpay_signature"]
            purchase.save()

            course = models.Course.objects.get(id=data["course_id"])
            user = request.user

            user.profile.purchased_courses.add(course)
            user.profile.save()

            return response.Response({"status": "Payment successful"})
        except razorpay.errors.SignatureVerificationError:
            return response.Response(
                {"status": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST
            )
