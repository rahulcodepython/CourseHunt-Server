from rest_framework import serializers
from . import models


class BaseCouponSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(
        format="%b %d %Y", read_only=True
    )  # Common field
    expiry = serializers.DateField(format="%b %d %Y")  # Common field

    class Meta:
        model = models.CuponeCode
        fields = "__all__"


class CreateCouponSerializer(serializers.ModelSerializer):
    class Meta(BaseCouponSerializer.Meta): ...

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ListCouponSerializer(BaseCouponSerializer):
    class Meta(BaseCouponSerializer.Meta): ...


class ListTransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateField(
        format="%b %d %Y", read_only=True
    )  # Common field
    course = serializers.SerializerMethodField()

    class Meta:
        model = models.Purchase
        fields = [
            "id",
            "course",
            "user",
            "amount",
            "razorpay_order_id",
            "is_paid",
            "created_at",
        ]

    def get_course(self, obj):
        return obj.course.name
