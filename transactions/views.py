"""
This module contains views for handling transactions, payments, and coupons
in the CourseHunt application. It includes functionality for course checkout,
payment initiation, payment verification, coupon management, and transaction listing.
"""

from rest_framework import views, response, status, permissions
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from authentication.models import Profile
from server.message import Message
from server.decorators import catch_exception
from server.utils import pagination_next_url_builder
from . import serializers, models
import razorpay

# Initialize Razorpay client with API keys
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))


def calculate_course_price(price: int, offer: float) -> float:
    """
    Calculate the total course price after applying tax and offer.
    """
    tax: float = 0.18 * price  # 18% tax
    total: float = price + tax
    total -= (offer / 100 * total)  # Apply offer discount
    return total


class CourseCheckoutView(views.APIView):
    """
    View to handle course checkout and provide pricing details.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request, course_id: int):
        """
        Retrieve course pricing details for checkout.
        """
        # Check if the course exists
        course_exists: bool = models.Course.objects.filter(
            id=course_id).exists()
        if not course_exists:
            return Message.error("Course not found")

        # Fetch course and user details
        course: models.Course = models.Course.objects.get(id=course_id)
        user: Profile = request.user
        profile: Profile = user.profile

        # Calculate pricing details
        price: int = course.price
        total: float = calculate_course_price(price, course.offer)
        tax: float = 0.18 * price

        # Prepare response data
        response_data: dict = {
            "price": price,
            "tax": tax,
            "offer": course.offer,
            "total": total,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "country": profile.country,
            "city": profile.city,
            "phone": profile.phone,
            "address": profile.address,
        }

        return response.Response(response_data, status=status.HTTP_200_OK)


class InitiatePaymentView(views.APIView):
    """
    View to initiate payment for a course.
    """

    @catch_exception
    def post(self, request, course_id: int):
        """
        Create a Razorpay order and save it in the database.
        """
        # Check if the course exists
        course_exists: bool = models.Course.objects.filter(
            id=course_id).exists()
        if not course_exists:
            return Message.error("Course not found")

        # Fetch course and user details
        course: models.Course = models.Course.objects.get(id=course_id)
        user: Profile = request.user

        # Check if the user already purchased the course
        purchased_courses = Profile.objects.get(
            user=user).purchased_courses.all()
        if course in purchased_courses:
            return Message.error("You have already purchased this course")

        # Calculate total price
        total: float = calculate_course_price(course.price, course.offer)

        # Handle discount if applicable
        is_discount: bool = request.data.get("is_discount", False)
        discount: float = 0.0
        if is_discount:
            coupon_code_id: int = request.data.get("coupon_code")
            coupon_exists: bool = models.CouponCode.objects.filter(
                id=coupon_code_id).exists()
            if coupon_exists:
                coupon: models.CouponCode = models.CouponCode.objects.get(
                    id=coupon_code_id)
                discount = coupon.discount

        # Adjust total price after discount
        total = max(total - discount, 0)

        # Convert total to paisa for Razorpay
        amount: int = int(total * 100)

        # Create a Razorpay order
        razorpay_order: dict = razorpay_client.order.create(
            {"amount": amount, "currency": "INR", "payment_capture": "1"}
        )

        # Save the order in the database
        purchase_exists: bool = models.Purchase.objects.filter(
            razorpay_order_id=razorpay_order["id"], course=course, user=user
        ).exists()
        if not purchase_exists:
            models.Purchase.objects.create(
                course=course,
                user=user,
                amount=total,
                razorpay_order_id=razorpay_order["id"],
            )

        # Prepare response data
        response_data: dict = {
            "order_id": razorpay_order["id"],
            "amount": amount,
            "currency": "INR",
        }

        return response.Response(response_data, status=status.HTTP_201_CREATED)


class VerifyPaymentView(views.APIView):
    """
    View to verify Razorpay payment and update the purchase status.
    """

    def post(self, request):
        """
        Verify payment signature and update purchase details.
        """
        try:
            data: dict = request.data

            # Check if the order exists
            order_exists: bool = models.Purchase.objects.filter(
                razorpay_order_id=data["razorpay_order_id"]
            ).exists()
            if not order_exists:
                return Message.error("Order not found")

            # Fetch purchase details
            purchase: models.Purchase = models.Purchase.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )

            # Verify Razorpay payment signature
            razorpay_client.utility.verify_payment_signature(data)

            # Update purchase details
            purchase.is_paid = True
            purchase.razorpay_payment_id = data["razorpay_payment_id"]
            purchase.razorpay_signature = data["razorpay_signature"]
            purchase.save()

            # Handle coupon usage if applicable
            is_discount: bool = request.data.get("is_discount", False)
            if is_discount:
                coupon_code_id: int = request.data.get("coupon_code")
                coupon_exists: bool = models.CouponCode.objects.filter(
                    id=coupon_code_id).exists()
                if coupon_exists:
                    coupon: models.CouponCode = models.CouponCode.objects.get(
                        id=coupon_code_id)
                    coupon.used += 1
                    coupon.save()

            # Add course to user's purchased courses
            course: models.Course = models.Course.objects.get(
                id=data["course_id"])
            profile: Profile = Profile.objects.get(user=request.user)
            profile.purchased_courses.add(course)
            profile.save()

            return Message.success("Payment successful")

        except razorpay.errors.SignatureVerificationError:
            return Message.error("Invalid signature")


class CancelPaymentView(views.APIView):
    """
    View to handle payment cancellation.
    """

    @catch_exception
    def post(self, request):
        """
        Cancel a payment by deleting the associated purchase record.
        """
        # Extract Razorpay order ID from request data
        data: dict = request.data
        razorpay_order_id: str = data.get("razorpay_order_id")

        # Check if the purchase exists
        purchase_exists: bool = models.Purchase.objects.filter(
            razorpay_order_id=razorpay_order_id
        ).exists()
        if not purchase_exists:
            return Message.error("Order not found")

        # Fetch and delete the purchase record
        purchase: models.Purchase = models.Purchase.objects.get(
            razorpay_order_id=razorpay_order_id
        )
        purchase.delete()

        return Message.success("Payment cancelled")


class CreateCouponView(views.APIView):
    """
    View to create a new coupon. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request):
        """
        Create a new coupon using the provided data.
        """
        # Validate the request data using the serializer
        serializer = serializers.CreateCouponSerializer(data=request.data)
        if not serializer.is_valid():
            return Message.error(serializer.errors)

        # Save the new coupon
        serializer.save()

        # Fetch and serialize the newly created coupon
        new_coupon: models.CouponCode = models.CouponCode.objects.get(
            id=serializer.data["id"]
        )
        new_serializer = serializers.ListCouponSerializer(new_coupon)

        return response.Response(new_serializer.data, status=status.HTTP_200_OK)


class EditCouponView(views.APIView):
    """
    View to edit or delete an existing coupon. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def post(self, request, id: int):
        """
        Edit an existing coupon with the provided data.
        """
        # Fetch the coupon or return 404 if not found
        coupon: models.CouponCode = get_object_or_404(models.CouponCode, id=id)

        # Validate and update the coupon using the serializer
        serializer = serializers.CreateCouponSerializer(
            coupon, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Message.error(serializer.errors)

        serializer.save()

        # Fetch and serialize the updated coupon
        updated_coupon: models.CouponCode = models.CouponCode.objects.get(
            id=serializer.data["id"]
        )
        updated_serializer = serializers.ListCouponSerializer(updated_coupon)

        return response.Response(updated_serializer.data, status=status.HTTP_200_OK)

    @catch_exception
    def delete(self, request, id: int):
        """
        Delete an existing coupon.
        """
        # Fetch the coupon or return 404 if not found
        coupon: models.CouponCode = get_object_or_404(models.CouponCode, id=id)

        # Delete the coupon
        coupon.delete()

        return Message.success("Coupon is deleted")


class ListCouponView(views.APIView):
    """
    View to list all coupons with pagination. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        """
        Retrieve a paginated list of coupons.
        """
        # Extract pagination parameters from the request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Fetch and paginate the coupons
        coupons = models.CouponCode.objects.all().order_by("-id")
        paginator = Paginator(coupons, page_size)
        page = paginator.page(page_no)

        # Serialize the paginated coupons
        serializer = serializers.ListCouponSerializer(page, many=True)

        # Prepare the response data
        response_data: dict = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        return response.Response(response_data, status=status.HTTP_200_OK)


class ApplyCouponView(views.APIView):
    """
    View to apply a coupon to a course. Only accessible by authenticated users.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request, course_id: int):
        """
        Apply a coupon to a course and calculate the discounted price.
        """
        # Extract coupon code from the request data
        coupon_code: str = request.data.get("coupon_code")

        # Fetch the course or return 404 if not found
        course: models.Course = get_object_or_404(models.Course, id=course_id)

        # Check if the coupon exists
        coupon_exists: bool = models.CouponCode.objects.filter(
            code=coupon_code
        ).exists()
        if not coupon_exists:
            return Message.error("Coupon not found")

        # Fetch the coupon
        coupon: models.CouponCode = models.CouponCode.objects.get(
            code=coupon_code)

        # Validate the coupon's status and availability
        if not coupon.is_active:
            return Message.error("Coupon is not active")
        if coupon.expiry < timezone.now().date():
            return Message.error("Coupon is expired")
        if not coupon.is_unlimited and coupon.used >= coupon.quantity:
            return Message.error("Coupon is out of stock")

        # Calculate the discounted price
        discount: float = coupon.discount
        price: int = course.price
        total: float = calculate_course_price(price, course.offer)
        total = max(total - discount, 0)

        return response.Response(
            {
                "discount": discount,
                "total": total,
                "coupon_code_id": coupon.id,
            },
            status=status.HTTP_200_OK,
        )


class ListTransactionsView(views.APIView):
    """
    View to list all transactions with pagination. Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request):
        """
        Retrieve a paginated list of all transactions.
        """
        # Extract pagination parameters from the request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Generate a cache key for the transactions
        cache_key: str = f"transactions_{page_no}_{page_size}"

        # Check if the data is cached
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch and paginate the transactions
        purchases = models.Purchase.objects.all().order_by("-id")
        paginator = Paginator(purchases, page_size)
        page = paginator.page(page_no)

        # Serialize the paginated transactions
        serializer = serializers.ListTransactionSerializer(page, many=True)

        # Prepare the response data
        response_data: dict = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        # Cache the response data
        cache.set(cache_key, response_data, timeout=60)

        return response.Response(response_data, status=status.HTTP_200_OK)


class ListSelfTransactionsView(views.APIView):
    """
    View to list a user's transactions with pagination. Only accessible by authenticated users.
    """
    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def get(self, request):
        """
        Retrieve a paginated list of the user's transactions.
        """
        # Extract pagination parameters from the request
        page_no: int = int(request.GET.get("page", 1))
        page_size: int = int(request.GET.get("page_size", 2))

        # Generate a cache key for the user's transactions
        cache_key: str = f"self_transactions_{page_no}_{page_size}"

        # Check if the data is cached
        cached_data = cache.get(cache_key)
        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        # Fetch and paginate the user's transactions
        purchases = models.Purchase.objects.filter(
            user=request.user).order_by("-id")
        paginator = Paginator(purchases, page_size)
        page = paginator.get_page(page_no)

        # Serialize the paginated transactions
        serializer = serializers.ListTransactionSerializer(page, many=True)

        # Prepare the response data
        response_data: dict = {
            "results": serializer.data,
            "count": paginator.count,
            "next": pagination_next_url_builder(page, request.path),
        }

        # Cache the response data
        cache.set(cache_key, response_data, timeout=60)

        return response.Response(response_data, status=status.HTTP_200_OK)
