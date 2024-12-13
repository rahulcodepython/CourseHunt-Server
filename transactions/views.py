from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from authentication.models import Profile
from django.utils import timezone


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
        return response.Response({"error": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def error(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    def success(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_200_OK)

    def create(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_201_CREATED)


class CourseCheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            if not models.Course.objects.filter(id=course_id).exists():
                return Message.error("Course not found")

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
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(str(e))


class InitiatePaymentView(views.APIView):
    def post(self, request, course_id):
        try:
            if not models.Course.objects.filter(id=course_id).exists():
                return Message.error("Course not found")

            course = models.Course.objects.get(id=course_id)
            user = request.user

            if course in Profile.objects.get(user=request.user).purchased_courses.all():
                return Message.error("You have already purchased this course")

            total = calculateCoursePrice(course.price, course.offer)

            is_discount = request.data["is_discount"]
            discount = 0
            if is_discount:
                coupon_code_id = request.data["coupon_code"]
                if models.CuponeCode.objects.filter(id=coupon_code_id).exists():
                    coupon = models.CuponeCode.objects.get(id=coupon_code_id)
                    discount = coupon.discount

            total = total - discount if total > discount else 0

            amount = int(total * 100)  # Razorpay amount is in paisa

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
                    amount=total,
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
            return Message.error(str(e))


class VerifyPaymentView(views.APIView):
    def post(self, request):
        try:
            data = request.data
            if not models.Purchase.objects.filter(
                razorpay_order_id=data["razorpay_order_id"]
            ).exists():
                return Message.error("Order not found")

            purchase = models.Purchase.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )

            razorpay_client.utility.verify_payment_signature(data)
            purchase.is_paid = True
            purchase.razorpay_payment_id = data["razorpay_payment_id"]
            purchase.razorpay_signature = data["razorpay_signature"]
            purchase.save()

            is_discount = request.data["is_discount"]
            if is_discount:
                coupon_code_id = request.data["coupon_code"]
                if models.CuponeCode.objects.filter(id=coupon_code_id).exists():
                    coupon = models.CuponeCode.objects.get(id=coupon_code_id)
                    coupon.used += 1
                    coupon.save()

            course = models.Course.objects.get(id=data["course_id"])
            profile = Profile.objects.get(user=request.user)
            profile.purchased_courses.add(course)
            profile.save()

            return Message.success("Payment successful")

        except razorpay.errors.SignatureVerificationError:
            return Message.error("Invalid signature")


class CancelPaymentView(views.APIView):
    def post(self, request):
        try:
            data = request.data
            if not models.Purchase.objects.filter(
                razorpay_order_id=data["razorpay_order_id"]
            ).exists():
                return Message.error("Order not found")

            purchase = models.Purchase.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )

            purchase.delete()

            return Message.success("Payment cancelled")

        except Exception as e:
            return Message.error(str(e))


class CreateCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.CreateCouponSerializer(data=request.data)

            if not serializer.is_valid():
                return Message.error(serializer.errors)

            serializer.save()

            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Message.warn(str(e))


class EditCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, id):
        try:
            coupon = get_object_or_404(models.CuponeCode, id=id)
            serializer = serializers.CreateCouponSerializer(
                coupon, data=request.data, partial=True
            )

            if not serializer.is_valid():
                return Message.error(serializer.errors)

            serializer.save()

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))

    def delete(self, request, id):
        try:
            coupon = get_object_or_404(models.CuponeCode, id=id)
            coupon.delete()

            return Message.success("Coupon is deleted")

        except Exception as e:
            return Message.error(str(e))


class ListCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            coupons = models.CuponeCode.objects.all()
            serializer = serializers.ListCouponSerializer(coupons, many=True)

            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.warn(str(e))


class ApplyCouponView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            coupon = request.data.get("coupon_code")
            course = models.Course.objects.get(id=course_id)

            if not models.CuponeCode.objects.filter(code=coupon).exists():
                return Message.error("Coupon not found")

            coupon = models.CuponeCode.objects.get(code=coupon)

            if not coupon.is_active:
                return Message.error("Coupon is not active")

            if coupon.expiry < timezone.now().date():
                return Message.error("Coupon is expired")

            if not coupon.is_unlimited and coupon.used >= coupon.quantity:
                return Message.error("Coupon is out of stock")

            discount = coupon.discount

            price = course.price
            total = calculateCoursePrice(price, course.offer)
            total = total - discount if total > discount else 0

            return response.Response(
                {
                    "discount": discount,
                    "total": total,
                    "coupon_code_id": coupon.id,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(str(e))


class ListTransactionsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            purchases = models.Purchase.objects.all()
            # paginator = Paginator(purchases, 10)
            # page = request.GET.get("page")
            # purchases = paginator.get_page(page)
            serializer = serializers.ListTransactionSerializer(purchases, many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))


class ListSelfTransactionsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            purchases = models.Purchase.objects.filter(user=request.user)
            # paginator = Paginator(purchases, 10)
            # page = request.GET.get("page")
            # purchases = paginator.get_page(page)
            serializer = serializers.ListTransactionSerializer(purchases, many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(str(e))
