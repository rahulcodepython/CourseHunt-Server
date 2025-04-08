"""
This module defines URL patterns for transaction-related views in the CourseHunt application.
Each URL is mapped to a specific view for handling transactions, payments, and coupon management.
"""

from django.urls import path  # Importing path for defining URL patterns
from . import views  # Importing views from the current package

# Define URL patterns for transaction-related views
urlpatterns: list[path] = [
    # URL for course checkout
    path(
        "checkout/<str:course_id>/",  # URL pattern with course_id as a string parameter
        views.CourseCheckoutView.as_view(),  # View to handle course checkout
        name="checkout",  # Name of the URL pattern
    ),
    # URL for initiating payment
    path(
        # URL pattern with course_id as a string parameter
        "payment/initiate/<str:course_id>/",
        views.InitiatePaymentView.as_view(),  # View to handle payment initiation
        name="initiate-payment",  # Name of the URL pattern
    ),
    # URL for verifying payment
    path(
        "payment/verify/",  # URL pattern for payment verification
        views.VerifyPaymentView.as_view(),  # View to handle payment verification
        name="verify-payment",  # Name of the URL pattern
    ),
    # URL for canceling payment
    path(
        "payment/cancel/",  # URL pattern for payment cancellation
        views.CancelPaymentView.as_view(),  # View to handle payment cancellation
        name="payment-cancel",  # Name of the URL pattern
    ),
    # URL for creating a coupon code
    path(
        "create-coupon-code/",  # URL pattern for creating a coupon code
        views.CreateCouponView.as_view(),  # View to handle coupon creation
        name="create-coupon",  # Name of the URL pattern
    ),
    # URL for listing all coupon codes
    path(
        "list-coupon-code/",  # URL pattern for listing coupon codes
        views.ListCouponView.as_view(),  # View to handle listing of coupon codes
        name="list-coupon",  # Name of the URL pattern
    ),
    # URL for editing a coupon code
    path(
        "edit-coupon-code/<str:id>/",  # URL pattern with id as a string parameter
        views.EditCouponView.as_view(),  # View to handle coupon editing
        name="edit-coupon",  # Name of the URL pattern
    ),
    # URL for applying a coupon code
    path(
        # URL pattern with course_id as a string parameter
        "apply-coupon-code/<str:course_id>/",
        views.ApplyCouponView.as_view(),  # View to handle coupon application
        name="apply-coupon",  # Name of the URL pattern
    ),
    # URL for listing all transactions
    path(
        "list-transactions/",  # URL pattern for listing all transactions
        views.ListTransactionsView.as_view(),  # View to handle listing of transactions
        name="list-transactions",  # Name of the URL pattern
    ),
    # URL for listing self transactions
    path(
        "list-self-transactions/",  # URL pattern for listing self transactions
        # View to handle listing of self transactions
        views.ListSelfTransactionsView.as_view(),
        name="list-self-transactions",  # Name of the URL pattern
    ),
]
