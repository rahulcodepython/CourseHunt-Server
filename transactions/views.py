from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from . import serializers, models
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from authentication.models import Profile
from django.utils import timezone
from django.core.cache import cache
from server.message import Message
from server.decorators import catch_exception
from server.utils import pagination_next_url_builder

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY)
)


def calculateCoursePrice(price: int, offer: float) -> float:
    tax = 0.18 * price
    total = price + tax
    total = total - (offer / 100 * total)
    return total


class CourseCheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request, course_id):
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


class InitiatePaymentView(views.APIView):

    @catch_exception
    def post(self, request, course_id):
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

    @catch_exception
    def post(self, request):
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


class CreateCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request):
        serializer = serializers.CreateCouponSerializer(data=request.data)

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        new_coupon = models.CuponeCode.objects.get(id=serializer.data["id"])
        new_serializer = serializers.ListCouponSerializer(new_coupon)

        return response.Response(new_serializer.data, status=status.HTTP_200_OK)


class EditCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request, id):
        coupon = get_object_or_404(models.CuponeCode, id=id)
        serializer = serializers.CreateCouponSerializer(
            coupon, data=request.data, partial=True
        )

        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        updated_coupon = models.CuponeCode.objects.get(id=serializer.data["id"])
        updated_serializer = serializers.ListCouponSerializer(updated_coupon)

        return response.Response(updated_serializer.data, status=status.HTTP_200_OK)

    @catch_exception
    def delete(self, request, id):
        coupon = get_object_or_404(models.CuponeCode, id=id)
        coupon.delete()

        return Message.success("Coupon is deleted")


class ListCouponView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 2)

        coupons = models.CuponeCode.objects.all().order_by("-id")
        paginator = Paginator(coupons, page_size)
        page = paginator.page(page_no)

        serializer = serializers.ListCouponSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class ApplyCouponView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request, course_id):
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


class ListTransactionsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 2)

        cache_key = f"transactions_{page_no}_{page_size}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        purchases = models.Purchase.objects.all().order_by("-id")
        paginator = Paginator(purchases, page_size)
        page = paginator.page(page_no)

        serializer = serializers.ListTransactionSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(cache_key, response_data, timeout=60)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class ListSelfTransactionsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request):
        page_no = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 2)

        cache_key = f"self_transactions_{page_no}_{page_size}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        purchases = models.Purchase.objects.filter(user=request.user).order_by("-id")
        paginator = Paginator(purchases, page_size)
        page = paginator.get_page(page_no)

        serializer = serializers.ListTransactionSerializer(page, many=True)

        response_data = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        cache.set(cache_key, response_data, timeout=60)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )
