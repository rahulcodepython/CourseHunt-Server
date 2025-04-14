from typing import List
from django.urls import path
from django.urls.resolvers import URLPattern
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

# URL patterns for user management
USER_MANAGEMENT_PATTERNS: List[URLPattern] = [
    path("users/me/", views.UserViews.as_view(), name="user_profile"),
    path("users/alluser/", views.ListAllUser.as_view(), name="user_list"),
]

# URL patterns for user activation
ACTIVATION_PATTERNS: List[URLPattern] = [
    path("users/activate/", views.ActivateUserViews.as_view(), name="user_activate"),
    path(
        "users/activate/email/resend/",
        views.ResendActivateUserViews.as_view(),
        name="resend_activation"
    ),
]

# URL patterns for authentication
AUTH_PATTERNS: List[URLPattern] = [
    path("users/login/email/", views.SendLoginOTPView.as_view(), name="send_otp"),
    path(
        "users/login/email/resend/",
        views.ResendLoginOTPView.as_view(),
        name="resend_otp"
    ),
]

# URL patterns for JWT operations
JWT_PATTERNS: List[URLPattern] = [
    path("users/jwt/create/", views.CreateJWTView.as_view(), name="token_create"),
    path("users/jwt/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    path("users/jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

# URL patterns for user data management
USER_DATA_PATTERNS: List[URLPattern] = [
    path(
        "users/reset_password/",
        views.ResetUserPassword.as_view(),
        name="reset_password"
    ),
    path("users/reset/email/", views.ResetUserEmail.as_view(), name="reset_email"),
    path("users/update-email/", views.UpdateEmailView.as_view(), name="update_email"),
    path("users/check-email/", views.CheckEmailView.as_view(), name="check_email"),
]

# URL patterns for OAuth providers
OAUTH_PATTERNS: List[URLPattern] = [
    path(
        "github/auth/",
        views.GithubAuthRedirect.as_view(),
        name="github_auth_redirect",
    ),
    path(
        "github/authenticate/",
        views.GithubAuthenticate.as_view(),
        name="github_authenticate",
    ),
    path(
        "google/auth/",
        views.GoogleAuthRedirect.as_view(),
        name="google_auth_redirect",
    ),
    path(
        "google/authenticate/",
        views.GoogleAuthenticate.as_view(),
        name="google_authenticate",
    ),
]

# Combine all URL patterns
urlpatterns: List[URLPattern] = [
    *USER_MANAGEMENT_PATTERNS,
    *ACTIVATION_PATTERNS,
    *AUTH_PATTERNS,
    *JWT_PATTERNS,
    *USER_DATA_PATTERNS,
    *OAUTH_PATTERNS,
]
