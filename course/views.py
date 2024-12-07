from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from authentication.models import Profile

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY)
)


def calculateCoursePrice(price: int, offer: float) -> float:
    tax = 0.18 * price
    total = price + tax
    total = total - (offer / 100 * total)
    return total


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
                print(serializer.errors)
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            course = serializer.save()

            return response.Response({"id": course.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ListCoursesView(views.APIView):
    def get(self, request):
        try:
            courses = models.Course.objects.all().filter(status="published")
            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            if request.user.is_authenticated:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": request.user}
                )
            else:
                serializer = serializers.ListCoursesSerializer(
                    courses, many=True, context={"user": None}
                )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
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

            serializer = serializers.ListCoursesAdminDashboardSerializer(
                courses, many=True
            )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class PurchasedListCoursesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = get_object_or_404(Profile, user=request.user)
            courses = profile.purchased_courses.all()

            # paginator = Paginator(courses, 10)
            # page = request.GET.get("page")
            # courses = paginator.get_page(page)

            serializer = serializers.ListCoursesDashboardSerializer(courses, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCourseView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            serializer = serializers.CreateCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

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

    def delete(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)
            course.delete()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ToggleCourseStatusView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)

            if course.status == "draft":
                course.status = "published"
            else:
                course.status = "draft"

            course.save()

            return response.Response({"id": course_id}, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class StudySingleCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            profile = Profile.objects.get(user=request.user)
            course = models.Course.objects.get(id=course_id)

            if course not in profile.purchased_courses.all():
                res = Message.error("Course not purchased")
                return response.Response(res["body"], status=res["status"])

            serializer = serializers.StudySingleCourseSerializer(course)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class DetailSingleCourseView(views.APIView):
    def get(self, request, course_id):
        try:
            course = models.Course.objects.get(id=course_id)

            if request.user.is_authenticated:
                serializer = serializers.DetailSingleCourseSerializer(
                    course, context={"user": request.user}
                )
            else:
                serializer = serializers.DetailSingleCourseSerializer(
                    course, context={"user": None}
                )

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class CourseCheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            if not models.Course.objects.filter(id=course_id).exists():
                res = Message.error("Course not found")
                return response.Response(res["body"], status=res["status"])

            course = models.Course.objects.get(id=course_id)
            user = request.user
            profile = user.profile

            price = course.price
            total = calculateCoursePrice(price, course.offer)
            tax = 0.18 * price

            return response.Response(
                {
                    "price": price,
                    "tax": tax,
                    "offer": course.offer,
                    "total": total,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "country": profile.country,
                    "city": profile.city,
                    "phone": profile.phone,
                    "address": profile.address,
                }
            )

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class InitiatePayment(views.APIView):
    def post(self, request, course_id):
        try:
            if not models.Course.objects.filter(id=course_id).exists():
                res = Message.error("Course not found")
                return response.Response(res["body"], status=res["status"])

            course = models.Course.objects.get(id=course_id)
            user = request.user

            if course in user.profile.purchased_courses.all():
                res = Message.error("Course already purchased")
                return response.Response(res["body"], status=res["status"])

            amount = int(
                calculateCoursePrice(course.price, course.offer) * 100
            )  # Razorpay amount is in paisa
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(
                {"amount": amount, "currency": "INR", "payment_capture": "1"}
            )
            # Create an Order in our DB
            if not models.Purchase.objects.filter(
                razorpay_order_id=razorpay_order["id"],
                course=course,
                user=user,
            ).exists():
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

        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class VerifyPayment(views.APIView):
    def post(self, request):
        try:
            data = request.data
            if not models.Purchase.objects.filter(
                razorpay_order_id=data["razorpay_order_id"]
            ).exists():
                return response.Response(
                    {"status": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )
            purchase = models.Purchase.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )

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


class CreateCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.CreateCouponSerializer(data=request.data)

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            serializer.save()

            return response.Response(
                {"msg": "Coupne is created."}, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class EditCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, id):
        try:
            coupon = get_object_or_404(models.CuponeCode, id=id)
            serializer = serializers.CreateCouponSerializer(coupon, data=request.data)

            if not serializer.is_valid():
                res = Message.error(serializer.errors)
                return response.Response(res["body"], status=res["status"])

            serializer.save()

            return response.Response(
                {"msg": "Coupne is updated."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])

    def delete(self, request, id):
        try:
            coupon = get_object_or_404(models.CuponeCode, id=id)
            coupon.delete()

            return response.Response(
                {"msg": "Coupne is deleted."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ListCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            coupons = models.CuponeCode.objects.all()
            serializer = serializers.ListCouponSerializer(coupons, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])
