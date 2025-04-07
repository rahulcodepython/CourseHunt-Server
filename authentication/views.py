from datetime import datetime, timedelta
from typing import Dict, Any, Optional, TypedDict, List
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from django.utils.timezone import localtime, now
from rest_framework import views, response, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import random
import string
import uuid
import requests
from . import serializers, email, models
from server.message import Message
from server.decorators import catch_exception
from server.utils import redirect_uri_builder

# Constants
TOKEN_LENGTH: int = 4
CACHE_TIMEOUT: int = 300
OTP_EXPIRY_MINUTES: int = 10


class TokenDict(TypedDict):
    """Type definition for JWT token response"""
    refresh: str
    access: str


# Get User model at module level
User = get_user_model()


def generate_random_code(length: int = TOKEN_LENGTH) -> str:
    """Generate a random alphanumeric code of specified length"""
    characters: str = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def get_tokens_for_user(user: models.User) -> TokenDict:
    """Generate JWT tokens with user information"""
    refresh = RefreshToken.for_user(user)

    # Add user claims to token
    user_claims = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "image": user.image,
        "is_superuser": user.is_superuser
    }
    refresh.payload.update(user_claims)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def check_email_exists(email: str) -> bool:
    """Check if email exists in database"""
    try:
        return User.objects.filter(email=email).exists()
    except Exception:
        return False


def check_user_active(email: str) -> bool:
    """Check if user account is active"""
    try:
        user = User.objects.get(email=email)
        return user.is_active
    except User.DoesNotExist:
        return False


def check_time_difference(recorded_time: datetime) -> bool:
    """Check if time difference is greater than OTP expiry time"""
    current_time: datetime = localtime(now())
    parsed_recorded_time: datetime = localtime(recorded_time)
    time_difference: timedelta = current_time - parsed_recorded_time
    return time_difference > timedelta(minutes=OTP_EXPIRY_MINUTES)


class BaseCodeMixin:
    """Mixin for common code generation methods"""

    def create_uid(self) -> str:
        """Generate unique UID"""
        max_attempts: int = 3
        for _ in range(max_attempts):
            uid: str = generate_random_code()
            if not self.model.objects.filter(uid=uid).exists():
                return uid
        raise ValueError("Failed to generate unique UID")

    def create_token(self) -> str:
        """Generate unique token"""
        max_attempts: int = 3
        for _ in range(max_attempts):
            token: str = generate_random_code()
            if not self.model.objects.filter(token=token).exists():
                return token
        raise ValueError("Failed to generate unique token")


class UserViews(BaseCodeMixin, views.APIView):
    """
    API View for user management operations.
    Handles user CRUD operations and profile management.
    """

    model = models.ActivationCode

    def check_authenticated_user(self, user: models.User) -> bool:
        """Verify user authentication status"""
        return user.is_authenticated

    @staticmethod
    def generate_unique_username(email: str) -> str:
        """Generate username from email"""
        base_username: str = email.split("@")[0]
        username: str = base_username
        counter: int = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    @catch_exception
    def get(self, request) -> response.Response:
        """Get user profile with caching"""
        if not self.check_authenticated_user(request.user):
            return Message.error(msg="You are not authenticated yet. Try again.")

        cache_key: str = f"login_{request.user.username}"
        cached_data: Optional[Dict] = cache.get(cache_key)

        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        serialized_data = serializers.UserSerializer(request.user).data
        cache.set(cache_key, serialized_data, timeout=CACHE_TIMEOUT)
        return response.Response(serialized_data, status=status.HTTP_200_OK)

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Create a new user account and send activation email.

        Args:
            request: HTTP request object containing user data

        Returns:
            Response with success/error message
        """
        email_address: str = request.data.get("email", "")

        # Check if email already exists
        if check_email_exists(email_address):
            if not check_user_active(email_address):
                return Message.warn(
                    msg="You have already registered. But not verified you email yet. Please verify it first."
                )
            return Message.warn(msg="You have already registered.")

        # Create user with generated username
        try:
            serialized_data = serializers.UserCreateSerializer(
                data={
                    **request.data,
                    "username": self.generate_unique_username(email_address),
                }
            )

            if not serialized_data.is_valid():
                return Message.error(
                    msg=f"Validation error: {serialized_data.errors}"
                )

            user = serialized_data.save()

            # Generate activation codes
            uid: str = self.create_uid()
            token: str = self.create_token()

            # Send activation email
            try:
                email.ActivationEmail(
                    uid=uid,
                    token=token,
                    email=user.email,
                    username=user.username,
                )
                # Create activation code record
                models.ActivationCode.objects.create(
                    user=user,
                    uid=uid,
                    token=token
                )
            except Exception as e:
                user.delete()  # Rollback user creation if email fails
                return Message.error(msg=f"Failed to send activation email: {str(e)}")

            return Message.create(msg="Your account has been created. Please verify your email.")

        except Exception as e:
            return Message.error(msg=f"Failed to create account: {str(e)}")

    @catch_exception
    def patch(self, request) -> response.Response:
        """
        Update user profile information.

        Args:
            request: HTTP request object containing update data

        Returns:
            Response with updated user data or error message
        """
        if not self.check_authenticated_user(request.user):
            return Message.error(msg="You are not authenticated yet. Try again.")

        try:
            serialized_data = serializers.UserUpdateSerializer(
                request.user,
                data=request.data,
                partial=True
            )

            if not serialized_data.is_valid():
                return Message.error(
                    msg=f"Validation error: {serialized_data.errors}"
                )

            updated_user = serialized_data.save()
            return response.Response(
                serializers.UserSerializer(updated_user).data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Message.error(msg=f"Failed to update profile: {str(e)}")

    @catch_exception
    def delete(self, request) -> response.Response:
        """
        Delete user account.

        Args:
            request: HTTP request object

        Returns:
            Response with success/error message
        """
        if not self.check_authenticated_user(request.user):
            return Message.error(msg="You are not authenticated yet. Try again.")

        try:
            request.user.delete()
            return Message.success(msg="Your account has been deleted.")
        except Exception as e:
            return Message.error(msg=f"Failed to delete account: {str(e)}")


class ActivateUserViews(views.APIView):
    """Handle user account activation process."""

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Activate user account with provided activation codes.

        Args:
            request: HTTP request object containing activation codes

        Returns:
            Response with JWT tokens or error message
        """
        uid: str = request.data.get("uid", "")
        token: str = request.data.get("token", "")

        try:
            # Get activation code and associated user
            activation = models.ActivationCode.objects.filter(
                uid=uid,
                token=token
            ).select_related('user').first()

            if not activation:
                return Message.error(msg="Invalid activation code. Please try again.")

            user = activation.user
            user.is_active = True
            user.save()

            # Clean up activation code
            activation.delete()

            # Generate and return JWT tokens
            return response.Response(
                get_tokens_for_user(user),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(msg=f"Activation failed: {str(e)}")


class ResendActivateUserViews(BaseCodeMixin, views.APIView):
    """
    View for resending account activation emails.
    Handles regeneration and resending of activation codes.
    """

    model = models.ActivationCode

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Handle resend activation email request.

        Args:
            request: HTTP request containing user email

        Returns:
            Response with success/error message
        """
        user_email: str = request.data.get("email")

        # Validate email existence
        if not check_email_exists(user_email):
            return Message.error(msg="No such user exists. Please try again.")

        try:
            user: models.User = User.objects.get(email=user_email)

            # Check user activation status
            if check_user_active(user_email):
                return Message.warn(
                    msg="Account already verified. Please proceed to login."
                )

            # Handle existing activation code
            activation_code: Optional[models.ActivationCode] = (
                models.ActivationCode.objects.filter(user=user).first()
            )

            if activation_code:
                # Resend existing code
                email.ActivationEmail(
                    uid=activation_code.uid,
                    token=activation_code.token,
                    email=user.email,
                    username=user.username,
                )
            else:
                # Generate and send new code
                uid: str = self.create_uid()
                token: str = self.create_token()

                try:
                    email.ActivationEmail(
                        uid=uid,
                        token=token,
                        email=user.email,
                        username=user.username,
                    )
                    models.ActivationCode.objects.create(
                        user=user,
                        uid=uid,
                        token=token
                    )
                except Exception as e:
                    return Message.error(
                        msg=f"Failed to send activation email: {str(e)}"
                    )

            return Message.success(msg="Activation link has been sent to your email.")

        except Exception as e:
            return Message.error(msg=f"Failed to process request: {str(e)}")


class SendLoginOTPView(BaseCodeMixin, views.APIView):
    """
    View for sending login OTP codes.
    Handles generation and sending of OTP codes for login.
    """

    model = models.LoginCode

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Handle login OTP request.

        Args:
            request: HTTP request containing user email

        Returns:
            Response with success/error message
        """
        user_email: str = request.data.get("email")

        try:
            # Validate user existence
            user: models.User = User.objects.filter(email=user_email).first()
            if not user:
                return Message.error(msg="No such user exists. Please try again.")

            # Check user activation status
            if not user.is_active:
                return Message.warn(
                    msg="Account not verified. Please verify your email first."
                )

            # Handle existing login code
            login_code: Optional[models.LoginCode] = (
                models.LoginCode.objects.filter(user=user).first()
            )

            if login_code:
                # Resend existing code
                email.LoginConfirmation(
                    uid=login_code.uid,
                    token=login_code.token,
                    email=user.email,
                    username=user.username,
                )
            else:
                # Generate and send new code
                uid: str = self.create_uid()
                token: str = self.create_token()

                try:
                    email.LoginConfirmation(
                        uid=uid,
                        token=token,
                        email=user.email,
                        username=user.username,
                    )
                    models.LoginCode.objects.create(
                        user=user,
                        uid=uid,
                        token=token
                    )
                except Exception as e:
                    return Message.error(
                        msg=f"Failed to send login code: {str(e)}"
                    )

            return Message.success(msg="Login code has been sent to your email.")

        except Exception as e:
            return Message.error(msg=f"Failed to process request: {str(e)}")


class ResendLoginOTPView(BaseCodeMixin, views.APIView):
    """
    View for resending login OTP codes.
    Handles regeneration and resending of login OTP codes.
    """

    model = models.LoginCode


class CreateJWTView(views.APIView):
    """Handle JWT token creation for both password and OTP-based authentication."""

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Create JWT tokens for user authentication.

        Args:
            request: HTTP request containing either email/password or OTP credentials

        Returns:
            Response with JWT tokens or error message
        """
        if not settings.OTP_VERIFICATION_LOGIN:
            # Password-based authentication
            email: str = request.data.get("email", "")
            password: str = request.data.get("password", "")

            try:
                # Validate user existence and status
                user: Optional[models.User] = User.objects.filter(
                    email=email).first()
                if not user:
                    return Message.error(msg="No such user exists. Please try again.")

                if not user.is_active:
                    return Message.warn(
                        msg="Account not verified. Please verify your email first."
                    )

                # Authenticate user
                authenticated_user: Optional[models.User] = authenticate(
                    username=user.username,
                    password=password
                )
                if not authenticated_user:
                    return Message.error(
                        msg="Invalid email or password. Please try again."
                    )

                # Generate and return tokens
                return response.Response(
                    get_tokens_for_user(authenticated_user),
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Message.error(msg=f"Authentication failed: {str(e)}")

        else:
            # OTP-based authentication
            uid: str = request.data.get("uid", "")
            token: str = request.data.get("token", "")

            try:
                # Validate OTP code
                login_code: Optional[models.LoginCode] = (
                    models.LoginCode.objects.filter(uid=uid, token=token)
                    .select_related('user')
                    .first()
                )

                if not login_code:
                    return Message.error(msg="Invalid login code. Please try again.")

                # Check OTP expiration
                if check_time_difference(login_code.created_at):
                    login_code.delete()
                    return Message.error(msg="Login code has expired. Please try again.")

                user: models.User = login_code.user

                # Validate user status
                if not user.is_active:
                    return Message.warn(
                        msg="Account not verified. Please verify your email first."
                    )

                # Clean up used OTP
                login_code.delete()

                # Generate and return tokens
                return response.Response(
                    get_tokens_for_user(user),
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Message.error(msg=f"Authentication failed: {str(e)}")


class TokenRefreshView(views.APIView):
    """Handle JWT token refresh operations."""

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Refresh JWT access token using refresh token.

        Args:
            request: HTTP request containing refresh token

        Returns:
            Response with new access token or error message
        """
        refresh_token: Optional[str] = request.data.get("refresh")

        if not refresh_token:
            return Message.error(msg="Refresh token not provided.")

        try:
            # Create refresh token instance
            token: RefreshToken = RefreshToken(refresh_token)

            # Get associated user
            user: models.User = User.objects.get(username=token["username"])

            # Update access token claims
            access_token = token.access_token
            user_claims: Dict[str, Any] = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "image": user.image,
                "is_superuser": user.is_superuser
            }
            access_token.update(user_claims)

            # Return new tokens
            return response.Response(
                {
                    "access": str(access_token),
                    "refresh": str(token),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(msg=f"Token refresh failed: {str(e)}")


class ResetUserPassword(BaseCodeMixin, views.APIView):
    """Handle password reset operations."""

    permission_classes = [permissions.IsAuthenticated]
    model = models.ResetPasswordCode

    @catch_exception
    def get(self, request) -> response.Response:
        """
        Generate and send password reset code.

        Args:
            request: HTTP request from authenticated user

        Returns:
            Response with success/error message
        """
        try:
            # Check for existing reset code
            reset_code: Optional[models.ResetPasswordCode] = (
                models.ResetPasswordCode.objects.filter(
                    user=request.user).first()
            )

            if reset_code:
                # Resend existing code
                email.ResetPasswordConfirmation(
                    uid=reset_code.uid,
                    token=reset_code.token,
                    email=request.user.email,
                    username=request.user.username,
                )
            else:
                # Generate and send new code
                uid: str = self.create_uid()
                token: str = self.create_token()

                try:
                    email.ResetPasswordConfirmation(
                        uid=uid,
                        token=token,
                        email=request.user.email,
                        username=request.user.username,
                    )
                    models.ResetPasswordCode.objects.create(
                        user=request.user,
                        uid=uid,
                        token=token
                    )
                except Exception as e:
                    return Message.error(
                        msg=f"Failed to send reset code: {str(e)}"
                    )

            return Message.success(msg="Password reset link sent to your email.")

        except Exception as e:
            return Message.error(msg=f"Password reset failed: {str(e)}")


class ResetUserEmail(BaseCodeMixin, views.APIView):
    """Handle email reset operations for authenticated users."""

    permission_classes = [permissions.IsAuthenticated]
    model = models.ResetEmailCode

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Generate and send email reset confirmation.

        Args:
            request: HTTP request containing new email

        Returns:
            Response with success/error message
        """
        new_email: str = request.data.get("email")
        if not new_email:
            return Message.error(msg="New email is required.")

        try:
            # Check for existing reset code
            reset_code: Optional[models.ResetEmailCode] = (
                models.ResetEmailCode.objects.filter(user=request.user).first()
            )

            if reset_code:
                # Resend existing code
                email.ResetEmailConfirmation(
                    uid=reset_code.uid,
                    token=reset_code.token,
                    email=new_email,
                    username=request.user.username,
                )
            else:
                # Generate and send new code
                uid: str = self.create_uid()
                token: str = self.create_token()

                try:
                    email.ResetEmailConfirmation(
                        uid=uid,
                        token=token,
                        email=new_email,
                        username=request.user.username,
                    )
                    models.ResetEmailCode.objects.create(
                        user=request.user,
                        uid=uid,
                        token=token,
                        new_email=new_email
                    )
                except Exception as e:
                    return Message.error(msg=f"Failed to send reset email: {str(e)}")

            return Message.success(msg="Reset email link has been sent.")

        except Exception as e:
            return Message.error(msg=f"Email reset failed: {str(e)}")


class UpdateEmailView(views.APIView):
    """Handle email update operations for authenticated users."""

    permission_classes = [permissions.IsAuthenticated]

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Update user email with verification code.

        Args:
            request: HTTP request containing verification codes

        Returns:
            Response with success/error message
        """
        uid: str = request.data.get("uid", "")
        token: str = request.data.get("token", "")

        try:
            # Validate reset code
            reset_code: Optional[models.ResetEmailCode] = (
                models.ResetEmailCode.objects.filter(uid=uid, token=token)
                .select_related('user')
                .first()
            )

            if not reset_code:
                return Message.error(msg="Invalid reset code. Please try again.")

            if reset_code.user != request.user:
                return Message.error(msg="Unauthorized access. Please try again.")

            # Update user email
            user: models.User = request.user
            user.email = reset_code.new_email
            user.save()

            # Clean up reset code
            reset_code.delete()

            return Message.success(msg="Email successfully updated.")

        except Exception as e:
            return Message.error(msg=f"Email update failed: {str(e)}")


class CheckEmailView(views.APIView):
    """Handle email availability checks."""

    @catch_exception
    def post(self, request) -> response.Response:
        """
        Check if email is available for registration.

        Args:
            request: HTTP request containing email

        Returns:
            Response with availability status
        """
        email: str = request.data.get("email", "")
        if not email:
            return Message.error(msg="Email is required.")

        try:
            # Case-insensitive email check
            is_taken: bool = User.objects.filter(email__iexact=email).exists()
            if is_taken:
                return Message.error(msg="Email is already taken. Please try another.")

            return Message.success(msg="Email is available.")

        except Exception as e:
            return Message.error(msg=f"Email check failed: {str(e)}")


class ListAllUser(views.APIView):
    """Handle user listing for admin users."""

    permission_classes = [permissions.IsAdminUser]

    @catch_exception
    def get(self, request) -> response.Response:
        """
        List all users with caching.

        Args:
            request: HTTP request from admin user

        Returns:
            Response with serialized user data
        """
        cache_key: str = "all_users"
        cached_data: Optional[List[Dict[str, Any]]] = cache.get(cache_key)

        if cached_data:
            return response.Response(cached_data, status=status.HTTP_200_OK)

        try:
            # Get and serialize all users
            users: List[models.User] = User.objects.all().order_by(
                '-date_joined')
            serialized_data: List[Dict[str, Any]] = (
                serializers.UserSerializer(users, many=True).data
            )

            # Cache the results
            cache.set(cache_key, serialized_data, timeout=CACHE_TIMEOUT)

            return response.Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(msg=f"Failed to fetch users: {str(e)}")


class GithubAuthRedirect(views.APIView):
    """Handle GitHub OAuth2 authentication redirect."""

    @catch_exception
    def get(self, request, format: Optional[str] = None) -> response.Response:
        """
        Generate GitHub OAuth2 authorization URL.

        Args:
            request: HTTP request object
            format: Response format (optional)

        Returns:
            Response with GitHub authorization URL
        """
        # Generate unique state token
        state: str = str(uuid.uuid4())
        cache_timeout: int = 300  # 5 minutes

        # Store state in cache for validation
        cache.set(f"github_oauth_state_{state}", True, timeout=cache_timeout)

        # Build authorization URL
        auth_params: Dict[str, str] = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri_builder("github"),
            "scope": "user",
            "state": state
        }

        github_auth_url: str = (
            "https://github.com/login/oauth/authorize/?"
            + "&".join(f"{key}={value}" for key, value in auth_params.items())
        )

        return response.Response(
            {"url": github_auth_url},
            status=status.HTTP_200_OK
        )


class GithubAuthenticate(views.APIView):
    """Handle GitHub OAuth2 authentication callback."""

    @catch_exception
    def get(self, request, format: Optional[str] = None) -> response.Response:
        """
        Process GitHub OAuth2 callback and authenticate user.

        Args:
            request: HTTP request object containing authorization code
            format: Response format (optional)

        Returns:
            Response with JWT tokens or error message
        """
        # Validate required parameters
        code: Optional[str] = request.GET.get("code")
        state: Optional[str] = request.GET.get("state")

        if not code:
            return Message.error(msg="Authorization code not provided")
        if not state:
            return Message.error(msg="State parameter is missing")

        # Validate state token
        state_key: str = f"github_oauth_state_{state}"
        if not cache.get(state_key):
            return Message.error(msg="Invalid or expired state parameter")
        cache.delete(state_key)

        try:
            # Exchange code for access token
            token_data: Dict[str, str] = {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri_builder("github"),
            }

            token_response = requests.post(
                "https://github.com/login/oauth/access_token",
                data=token_data,
                headers={"Accept": "application/json"},
                timeout=10  # Add timeout
            )
            token_response.raise_for_status()  # Raise exception for bad responses

            access_token: Optional[str] = token_response.json().get(
                "access_token")
            if not access_token:
                return Message.error(msg="Failed to obtain access token")

            # Fetch user data from GitHub
            user_response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            user_response.raise_for_status()
            user_data: Dict[str, Any] = user_response.json()

            # Extract GitHub username
            github_username: str = user_data.get("login", "")
            if not github_username:
                return Message.error(msg="Failed to get GitHub username")

            try:
                # Check if user exists
                user: models.User = User.objects.get(username=github_username)
                tokens: TokenDict = get_tokens_for_user(user)
                return response.Response(tokens, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                # Create new user
                user_info: Dict[str, Any] = {
                    "email": user_data.get("email"),
                    "username": github_username,
                    "first_name": user_data.get("name", "").split()[0] if user_data.get("name") else "",
                    "last_name": " ".join(user_data.get("name", "").split()[1:]) if user_data.get("name") else "",
                    "image": user_data.get("avatar_url"),
                    "method": "Github",
                    "is_active": True,
                }

                # Create and save user
                user = User.objects.create_user(**user_info)
                user.set_password(user_data.get("node_id", uuid.uuid4().hex))
                user.save()

                # Generate tokens
                tokens: TokenDict = get_tokens_for_user(user)
                return response.Response(tokens, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Message.error(msg=f"GitHub API request failed: {str(e)}")
        except Exception as e:
            return Message.error(msg=f"Authentication failed: {str(e)}")


class GoogleAuthRedirect(views.APIView):
    """Handle Google OAuth2 authentication redirect."""

    @catch_exception
    def get(self, request, format: Optional[str] = None) -> response.Response:
        """
        Generate Google OAuth2 authorization URL.

        Args:
            request: HTTP request object
            format: Response format (optional)

        Returns:
            Response with Google authorization URL
        """
        try:
            # Build authorization parameters
            auth_params: Dict[str, str] = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": redirect_uri_builder("google"),
                "scope": "email profile",
                "response_type": "code"
            }

            # Construct authorization URL
            google_auth_url: str = (
                "https://accounts.google.com/o/oauth2/v2/auth?"
                + "&".join(f"{key}={value}" for key,
                           value in auth_params.items())
            )

            return response.Response(
                {"url": google_auth_url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Message.error(msg=f"Failed to generate auth URL: {str(e)}")


class GoogleAuthenticate(views.APIView):
    """Handle Google OAuth2 authentication callback."""

    @catch_exception
    def get(self, request, format: Optional[str] = None) -> response.Response:
        """
        Process Google OAuth2 callback and authenticate user.

        Args:
            request: HTTP request object containing authorization code
            format: Response format (optional)

        Returns:
            Response with JWT tokens or error message
        """
        # Validate authorization code
        code: Optional[str] = request.GET.get("code")
        if not code:
            return Message.error(msg="Authorization code not provided")

        try:
            # Exchange code for access token
            token_data: Dict[str, str] = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri_builder("google"),
                "grant_type": "authorization_code",
            }

            # Request access token
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data=token_data,
                timeout=10
            )
            token_response.raise_for_status()

            access_token: Optional[str] = token_response.json().get(
                "access_token")
            if not access_token:
                return Message.error(msg="Failed to obtain access token")

            # Fetch user data from Google
            user_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            user_response.raise_for_status()
            user_data: Dict[str, Any] = user_response.json()

            # Extract email (required field)
            google_email: Optional[str] = user_data.get("email")
            if not google_email:
                return Message.error(msg="Email not provided by Google")

            try:
                # Check if user exists
                user: models.User = User.objects.get(email=google_email)
                tokens: TokenDict = get_tokens_for_user(user)
                return response.Response(tokens, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                # Create new user
                user_info: Dict[str, Any] = {
                    "email": google_email,
                    "username": google_email.split("@")[0],
                    "first_name": user_data.get("given_name", ""),
                    "last_name": user_data.get("family_name", ""),
                    "image": user_data.get("picture"),
                    "method": "Google",
                    "is_active": True,
                }

                # Create and save user
                user = User.objects.create_user(**user_info)
                user.set_password(user_data.get("id", uuid.uuid4().hex))
                user.save()

                # Generate tokens
                tokens: TokenDict = get_tokens_for_user(user)
                return response.Response(tokens, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Message.error(msg=f"Google API request failed: {str(e)}")
        except Exception as e:
            return Message.error(msg=f"Authentication failed: {str(e)}")
