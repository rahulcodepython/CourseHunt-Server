from django.urls import path
from . import views

urlpatterns = [
    path("users/me/", views.UserViews.as_view()),
    path("users/activation/", views.ActivateUserViews.as_view()),
    path("users/resend_activation/", views.ResendActivateUserViews.as_view()),
    path("users/jwt/create/", views.CreateJWT.as_view()),
    path("users/jwt/refresh/", views.TokenRefreshView.as_view()),
    path("users/jwt/verify/", views.TokenVerifyView.as_view()),
    path("users/user/", views.UserDataView.as_view()),
    path("users/set_password/", views.ResetUserPassword.as_view()),
    path("users/set_email/", views.ResetUserEmail.as_view()),
    path("users/update_email/", views.UpdateEmailView.as_view()),
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
]
