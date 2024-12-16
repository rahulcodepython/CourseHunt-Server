from rest_framework_simplejwt.views import TokenVerifyView
from django.urls import path
from . import views

urlpatterns = [
    path("users/me/", views.UserViews.as_view()),
    path("users/activate/", views.ActivateUserViews.as_view()),
    path("users/activate/email/resend/", views.ResendActivateUserViews.as_view()),
    path("users/login/email/", views.SendLoginOTPView.as_view()),
    path("users/login/email/resend/", views.ResendLoginOTPView.as_view()),
    path("users/jwt/create/", views.CreateJWTView.as_view()),
    path("users/jwt/refresh/", views.TokenRefreshView.as_view()),
    path("users/jwt/verify/", TokenVerifyView.as_view()),
    path("users/reset_password/", views.ResetUserPassword.as_view()),
    path("users/reset/email/", views.ResetUserEmail.as_view()),
    path("users/update-email/", views.UpdateEmailView.as_view()),
    path("users/check-email/", views.CheckEmailView.as_view()),
    path(
        "github/auth/",
        views.github_auth_redirect.as_view(),
        name="github_auth_redirect",
    ),
    path(
        "github/authenticate/",
        views.github_authenticate.as_view(),
        name="github_authenticate",
    ),
    path(
        "google/auth/",
        views.google_auth_redirect.as_view(),
        name="google_auth_redirect",
    ),
    path(
        "google/authenticate/",
        views.google_authenticate.as_view(),
        name="google_authenticate",
    ),
    path("users/alluser/", views.ListAllUser.as_view()),
]
