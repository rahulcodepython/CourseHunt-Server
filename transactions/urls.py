from django.urls import path
from . import views

urlpatterns = [
    path(
        "checkout/<str:course_id>/", views.CourseCheckoutView.as_view(), name="checkout"
    ),
    path(
        "payment/initiate/<str:course_id>/",
        views.InitiatePayment.as_view(),
        name="initiate-payment",
    ),
    path("payment/verify/", views.VerifyPayment.as_view(), name="verify-payment"),
    path("payment/cancel/", views.CancelPayment.as_view(), name="payment-cancel"),
    path("create-coupon-code/", views.CreateCouponView.as_view(), name="create-coupon"),
    path("list-coupon-code/", views.ListCouponView.as_view(), name="list-coupon"),
    path(
        "edit-coupon-code/<str:id>/", views.EditCouponView.as_view(), name="edit-coupon"
    ),
    path(
        "apply-coupon-code/<str:course_id>/",
        views.ApplyCoupon.as_view(),
        name="apply-coupon",
    ),
]
