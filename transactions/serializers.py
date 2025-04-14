from rest_framework import serializers  # Importing serializers from DRF
from . import models  # Importing models from the current app


class BaseCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for Coupon model with common fields.
    """
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date and make it read-only
    )
    expiry: serializers.DateField = serializers.DateField(
        format="%b %d %Y"  # Format date for expiry field
    )

    class Meta:
        """
        Meta class for BaseCouponSerializer.
        """
        model = models.CouponCode  # Specify the model
        fields = "__all__"  # Include all fields from the model


class CreateCouponSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new coupon.
    Inherits common fields and behavior from BaseCouponSerializer.
    """
    class Meta(BaseCouponSerializer.Meta):
        pass  # Inherit Meta from BaseCouponSerializer

    def create(self, validated_data: dict) -> models.CouponCode:
        """
        Create a new coupon instance.
        """
        try:
            return super().create(validated_data)  # Call parent create method
        except Exception as e:
            raise serializers.ValidationError(
                {"error": f"Failed to create coupon: {str(e)}"}
            )  # Handle runtime errors gracefully

    def update(self, instance: models.CouponCode, validated_data: dict) -> models.CouponCode:
        """
        Update an existing coupon instance.
        """
        try:
            return super().update(instance, validated_data)  # Call parent update method
        except Exception as e:
            raise serializers.ValidationError(
                {"error": f"Failed to update coupon: {str(e)}"}
            )  # Handle runtime errors gracefully


class ListCouponSerializer(BaseCouponSerializer):
    """
    Serializer for listing coupons.
    Inherits common fields and behavior from BaseCouponSerializer.
    """
    class Meta(BaseCouponSerializer.Meta):
        pass  # Inherit Meta from BaseCouponSerializer


class ListTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for listing transactions with additional fields.
    """
    created_at: serializers.DateField = serializers.DateField(
        format="%b %d %Y", read_only=True  # Format date and make it read-only
    )
    course: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for ListTransactionSerializer.
        """
        model = models.Purchase  # Specify the model
        fields = [
            "id",  # Transaction ID
            "course",  # Course name
            "user",  # User who made the purchase
            "amount",  # Transaction amount
            "razorpay_order_id",  # Razorpay order ID
            "is_paid",  # Payment status
            "created_at",  # Transaction creation date
        ]

    def get_course(self, obj: models.Purchase) -> str:
        """
        Get the name of the course associated with the transaction.
        """
        try:
            return obj.course.name  # Return course name
        except AttributeError:
            return "Unknown Course"  # Handle cases where course is None
