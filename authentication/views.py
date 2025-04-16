from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import views, response, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from server.message import Message
from server.decorators import catch_exception


class CreateJWTView(views.APIView):
    """Handle JWT token creation for both password and OTP-based authentication."""

    permission_classes = [permissions.AllowAny]

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Create JWT tokens for user authentication.

        Args:
            request: HTTP request containing either email/password or OTP credentials

        Returns:
            Response with JWT tokens or error message
        """
        # Password-based authentication
        username: str = request.data.get("username", "")
        password: str = request.data.get("password", "")

        # Authenticate user
        authenticated_user = authenticate(
            username=username,
            password=password
        )

        if authenticated_user is None:
            return Message.error(
                msg="Invalid username or password. Please try again."
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(authenticated_user)
        access_token = str(refresh.access_token)

        # Set tokens in cookies
        response = Message.success(
            msg="Authentication successful.",
        )
        response.set_cookie(
            key="access",
            value=access_token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )

        return response
