from django.contrib import admin
from .models import Purchase, CouponCode  # Import only required models


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Purchase model.
    Displays relevant fields in the admin panel.
    """
    # Fields to display in the admin list view
    list_display: tuple[str, str, str, str] = (
        "course",  # Course associated with the purchase
        "user",    # User who made the purchase
        "amount",  # Amount paid for the purchase
        "is_paid",  # Payment status
    )


@admin.register(CouponCode)
class CouponCodeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CouponCode model.
    Displays relevant fields in the admin panel.
    """
    # Fields to display in the admin list view
    list_display: tuple[str, str, str, str, str, str, str] = (
        "code",          # Coupon code
        "discount",      # Discount percentage or amount
        "expiry",        # Expiry date of the coupon
        "quantity",      # Total quantity of the coupon
        "used",          # Number of times the coupon has been used
        "is_unlimited",  # Whether the coupon has unlimited usage
        "is_active",     # Whether the coupon is currently active
    )
