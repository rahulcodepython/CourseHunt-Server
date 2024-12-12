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
        return {"body": {"message": msg}, "status": status.HTTP_406_NOT_ACCEPTABLE}

    def error(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_400_BAD_REQUEST}

    def success(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_200_OK}

    def create(msg: str) -> object:
        return {"body": {"message": msg}, "status": status.HTTP_201_CREATED}


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

            if course in Profile.objects.get(user=request.user).purchased_courses.all():
                res = Message.error("Course already purchased")
                return response.Response(res["body"], status=res["status"])

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
                    amount=amount,
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

            return response.Response({"status": "Payment successful"})
        except razorpay.errors.SignatureVerificationError:
            return response.Response(
                {"status": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST
            )


class CancelPayment(views.APIView):
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

            purchase.delete()

            return response.Response({"status": "Payment cancelled"})
        except Exception as e:
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


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
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])


class ApplyCoupon(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            coupon = request.data.get("coupon_code")
            course = models.Course.objects.get(id=course_id)

            if not models.CuponeCode.objects.filter(code=coupon).exists():
                res = Message.error("Coupon not found")
                return response.Response(res["body"], status=res["status"])

            coupon = models.CuponeCode.objects.get(code=coupon)

            if not coupon.is_active:
                res = Message.error("Coupon not active")
                return response.Response(res["body"], status=res["status"])

            if coupon.expiry < timezone.now().date():
                res = Message.error("Coupon expired")
                return response.Response(res["body"], status=res["status"])

            if not coupon.is_unlimited and coupon.used >= coupon.quantity:
                res = Message.error("Coupon limit exceeded")
                return response.Response(res["body"], status=res["status"])

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
            print(e)
            res = Message.warn(str(e))
            return response.Response(res["body"], status=res["status"])
