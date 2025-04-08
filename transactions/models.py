from django.db import models  # Importing Django's models for ORM
from course.models import Course  # Importing Course model
from authentication.models import User  # Importing User model
import uuid  # Importing uuid for generating unique IDs


class Purchase(models.Model):
    """
    Represents a purchase made by a user for a course.
    Tracks payment details and purchase status.
    """
    id: str = models.CharField(
        primary_key=True,  # Marks this field as the primary key
        unique=True,  # Ensures the value is unique
        max_length=120,  # Maximum length of the field
        editable=False  # Prevents editing in admin or forms
    )
    course: Course = models.ForeignKey(
        Course,  # Links to the Course model
        on_delete=models.CASCADE  # Deletes purchase if the course is deleted
    )
    user: User = models.ForeignKey(
        User,  # Links to the User model
        on_delete=models.CASCADE  # Deletes purchase if the user is deleted
    )
    amount: float = models.DecimalField(
        max_digits=10,  # Maximum number of digits
        decimal_places=2  # Number of decimal places
    )
    razorpay_order_id: str | None = models.CharField(
        max_length=100,  # Maximum length of the field
        blank=True,  # Allows the field to be blank
        null=True  # Allows the field to be null
    )
    razorpay_payment_id: str | None = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    razorpay_signature: str | None = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    is_paid: bool = models.BooleanField(
        default=False  # Default value is False
    )
    created_at: str = models.DateField(
        auto_now_add=True  # Automatically sets the field to now when created
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate a unique ID if not already set.
        """
        if not self.id:  # Check if ID is not set
            self.id = str(uuid.uuid4())  # Generate a unique UUID
        super().save(*args, **kwargs)  # Call the parent class's save method


class CouponCode(models.Model):
    """
    Represents a coupon code for discounts on purchases.
    Tracks usage, expiry, and availability.
    """
    id: str = models.CharField(
        primary_key=True,
        unique=True,
        max_length=120,
        editable=False
    )
    code: str = models.CharField(
        max_length=10,  # Maximum length of the coupon code
        unique=True  # Ensures the code is unique
    )
    discount: int = models.IntegerField(
        help_text="Discount percentage offered by the coupon"  # Adds clarity
    )
    expiry: str = models.DateField(
        help_text="Expiry date of the coupon"  # Adds clarity
    )
    created_at: str = models.DateField(
        auto_now_add=True  # Automatically sets the field to now when created
    )
    quantity: int | None = models.IntegerField(
        null=True,  # Allows the field to be null
        blank=True,  # Allows the field to be blank
        help_text="Total quantity of coupons available"  # Adds clarity
    )
    used: int = models.IntegerField(
        default=0,  # Default value is 0
        help_text="Number of coupons used so far"  # Adds clarity
    )
    is_unlimited: bool = models.BooleanField(
        default=False,  # Default value is False
        help_text="Indicates if the coupon has unlimited usage"  # Adds clarity
    )
    is_active: bool = models.BooleanField(
        default=True,  # Default value is True
        help_text="Indicates if the coupon is currently active"  # Adds clarity
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the coupon code.
        """
        return self.code

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate a unique ID if not already set.
        """
        if not self.id:  # Check if ID is not set
            self.id = str(uuid.uuid4())  # Generate a unique UUID
        super().save(*args, **kwargs)  # Call the parent class's save method
