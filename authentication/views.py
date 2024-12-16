from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from rest_framework import views, response, status, permissions
from django.conf import settings
from . import serializers, email, models, tokens
import requests
import uuid
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils.timezone import localtime, now

User = get_user_model()


class Message:
    def warn(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def error(msg: str) -> object:
        return response.Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    def success(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_200_OK)

    def create(msg: str) -> object:
        return response.Response({"success": msg}, status=status.HTTP_201_CREATED)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def check_email_exists(email):
    return User.objects.filter(email=email).exists()


def check_authenticated_user(user):
    return user.is_authenticated


def check_user_active(email: str) -> bool:
    user = User.objects.get(email=email)
    return user.is_active


def check_time_difference(recorded_time) -> bool:
    current_time = localtime(now())
    parsed_recorded_time = localtime(recorded_time)
    time_difference = current_time - parsed_recorded_time
    return time_difference > timedelta(minutes=10)


class UserViews(views.APIView):
    def create_uid(self) -> int:
        uid: int = tokens.generate_random_code()
        if models.ActivationCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self) -> int:
        token: int = tokens.generate_random_code()
        if models.ActivationCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    @staticmethod
    def generate_unique_username(email: str) -> str:
        return email.split("@")[0]

    def get(self, request):
        try:
            if not check_authenticated_user(request.user):
                return Message.error(msg="You are not authenticated yet. Try again.")

            serialized_data = serializers.UserSerializer(request.user)
            return response.Response(serialized_data.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(f"{e}")

    def post(self, request):
        try:
            if check_email_exists(request.data["email"]):
                if not check_user_active(request.data["email"]):
                    return Message.warn(
                        msg="You have already registered. But not verified you email yet. Please verify it first."
                    )

                return Message.warn(msg="You have already registered.")

            serialized_data = serializers.UserCreateSerializer(
                data={
                    **request.data,
                    "username": self.generate_unique_username(request.data["email"]),
                }
            )

            if not serialized_data.is_valid():
                return Message.error(msg="Your data is not valid. Try again.")

            user = serialized_data.save()

            uid = self.create_uid()
            token = self.create_token()

            email.ActivationEmail(
                uid=uid,
                token=token,
                email=user.email,
                username=user.username,
            )
            models.ActivationCode.objects.create(user=user, uid=uid, token=token)

            return Message.create(
                msg="Your account has been creates. At First verify it."
            )

        except Exception as e:
            return Message.error(f"{e}")

    def patch(self, request):
        try:
            if not check_authenticated_user(request.user):
                return Message.error(msg="You are not authenticated yet. Try again.")

            serialized_data = serializers.UserUpdateSerializer(
                request.user, data=request.data, partial=True
            )

            if not serialized_data.is_valid():
                return Message.error(msg="Your data is not valid. Try again.")

            serialized_data.save()

            return response.Response(
                serializers.UserSerializer(request.user).data, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Message.error(f"{e}")

    def delete(self, request):
        try:
            if not check_authenticated_user(request.user):
                return Message.error(msg="You are not authenticated yet. Try again.")

            request.user.delete()

            return Message.success(msg="Your account has been deleted.")

        except Exception as e:
            return Message.error(f"{e}")


class ActivateUserViews(views.APIView):
    def post(self, request):
        try:
            uid = request.data["uid"]
            token = request.data["token"]
            user = (
                models.ActivationCode.objects.filter(uid=uid, token=token)[0].user
                if models.ActivationCode.objects.filter(uid=uid, token=token).exists()
                else None
            )

            if user is None:
                return Message.error(msg="You have entered wrong code. Try again.")

            user.is_active = True
            user.save()
            models.ActivationCode.objects.filter(uid=uid, token=token)[0].delete()

            return response.Response(
                {
                    **get_tokens_for_user(user),
                    "user": serializers.UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(f"{e}")


class ResendActivateUserViews(views.APIView):
    def create_uid(self):
        uid = tokens.generate_random_code()
        if models.ActivationCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.generate_random_code()
        if models.ActivationCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            user_email = request.data["email"]

            if not check_email_exists(user_email):
                return Message.error(msg="No such user is there. Try again.")

            user = User.objects.get(email=user_email)

            if check_user_active(user_email):
                return Message.warn(
                    msg="You have already registered. But not verified you email yet. Please verify it first."
                )

            if models.ActivationCode.objects.filter(user=user).exists():
                activation_code = models.ActivationCode.objects.get(user=user)
                email.ActivationEmail(
                    uid=activation_code.uid,
                    token=activation_code.token,
                    email=user.email,
                    username=user.username,
                )
            else:
                uid = self.create_uid()
                token = self.create_token()

                email.ActivationEmail(
                    uid=uid,
                    token=token,
                    email=user.email,
                    username=user.username,
                )
                activation_code = models.ActivationCode.objects.create(
                    user=user, uid=uid, token=token
                )

            return Message.success(msg="Activation link is sent to your mail.")

        except Exception as e:
            return Message.error(f"{e}")


class SendLoginOTPView(views.APIView):
    def create_uid(self):
        uid = tokens.generate_random_code()
        if models.LoginCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.generate_random_code()
        if models.LoginCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            user_email = request.data["email"]

            if not User.objects.filter(email=user_email).exists():
                return Message.error(msg="No such user is there. Try again.")

            user = User.objects.get(email=user_email)

            if not user.is_active:
                return Message.warn(
                    msg="You have already registered. But not verified you email yet. Please verify it first."
                )

            if models.LoginCode.objects.filter(user=user).exists():
                login_code = models.LoginCode.objects.get(user=user)
                email.LoginConfirmation(
                    uid=login_code.uid,
                    token=login_code.token,
                    email=user.email,
                    username=user.username,
                )
            else:
                uid = self.create_uid()
                token = self.create_token()

                email.LoginConfirmation(
                    uid=uid,
                    token=token,
                    email=user.email,
                    username=user.username,
                )
                models.LoginCode.objects.create(user=user, uid=uid, token=token)

            return Message.success(msg="Login code is sent to your email.")

        except Exception as e:
            print(str(e))
            return Message.error(f"{e}")


class ResendLoginOTPView(views.APIView):
    def create_uid(self):
        uid = tokens.generate_random_code()
        if models.LoginCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.generate_random_code()
        if models.LoginCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            user_email = request.data["email"]

            if not User.objects.filter(email=user_email).exists():
                return Message.error(msg="No such user is there. Try again.")

            user = User.objects.get(email=user_email)

            if not user.is_active:
                return Message.warn(
                    msg="You have already registered. But not verified you email yet. Please verify it first."
                )

            if models.LoginCode.objects.filter(user=user).exists():
                login_code = models.LoginCode.objects.get(user=user)
                email.LoginConfirmation(
                    uid=login_code.uid,
                    token=login_code.token,
                    email=user.email,
                    username=user.username,
                )
            else:
                uid = self.create_uid()
                token = self.create_token()

                email.LoginConfirmation(
                    uid=uid,
                    token=token,
                    email=user.email,
                    username=user.username,
                )
                models.LoginCode.objects.create(user=user, uid=uid, token=token)

            return Message.success(msg="Login code is again sent to your email.")

        except Exception as e:
            return Message.error(f"{e}")


class CreateJWTView(views.APIView):
    def post(self, request):
        try:
            if settings.OTP_VERIFICATION_LOGIN is False:
                email = request.data["email"]
                password = request.data["password"]

                if not User.objects.filter(email=email).exists():
                    return Message.error(msg="No such user is there. Try again.")

                username = User.objects.get(email=email).username

                if not user.is_active:
                    return Message.warn(
                        msg="You have already registered. But not verified you email yet. Please verify it first."
                    )

                user = authenticate(username=username, password=password)

                if user is None:
                    return Message.error(
                        msg="Your email or password is not correct. Try again."
                    )

            else:
                uid = request.data["uid"]
                token = request.data["token"]

                if not models.LoginCode.objects.filter(uid=uid, token=token).exists():
                    return Message.error(msg="You have entered wrong code. Try again.")

                login_code = models.LoginCode.objects.filter(uid=uid, token=token)[0]

                if check_time_difference(login_code.created_at):
                    login_code.delete()
                    return Message.error(msg="Your code is expired. Try again.")

                user = login_code.user

                if not user.is_active:
                    return Message.warn(
                        msg="You have already registered. But not verified you email yet. Please verify it first."
                    )

                login_code.delete()

            return response.Response(
                {
                    **get_tokens_for_user(user),
                    "user": serializers.UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Message.error(f"{e}")


class TokenRefreshView(views.APIView):
    def post(self, request):
        try:
            refresh = request.data.get("refresh")

            if refresh is None:
                return Message.error(msg="No refresh token is provided. Try again.")

            token = RefreshToken(refresh)

            user = User.objects.get(username=token["username"])

            return response.Response(
                {
                    "access": str(token.access_token),
                    "refresh": str(token),
                    "user": serializers.UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Message.error(f"{e}")


class ResetUserPassword(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def create_uid(self):
        uid = tokens.generate_random_code()
        if models.ResetPasswordCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.generate_random_code()
        if models.ResetPasswordCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def get(self, request):
        try:
            if models.ResetPasswordCode.objects.filter(user=request.user).exists():
                reset_password_code = models.ResetPasswordCode.objects.get(
                    user=request.user
                )

                email.ResetPasswordConfirmation(
                    uid=reset_password_code.uid,
                    token=reset_password_code.token,
                    email=request.user.email,
                    username=request.user.username,
                )

            else:
                uid = self.create_uid()
                token = self.create_token()

                email.ResetPasswordConfirmation(
                    uid=uid,
                    token=token,
                    email=request.user.email,
                    username=request.user.username,
                )

                reset_password_code = models.ResetPasswordCode.objects.create(
                    user=request.user, uid=uid, token=token
                )

            return Message.success(msg="Reset Password link is sent to your email.")

        except Exception as e:
            return Message.error(f"{e}")

    def post(self, request):
        try:
            new_password = request.data["newPassword"]
            current_password = request.data["oldPassword"]
            uid = request.data["uid"]
            token = request.data["token"]

            if not models.ResetPasswordCode.objects.filter(
                uid=uid, token=token
            ).exists():
                return Message.error(msg="You have entered wrong code. Try again.")

            reset_password_code = models.ResetPasswordCode.objects.filter(
                uid=uid, token=token
            )[0]

            user = request.user

            if reset_password_code.user != user:
                return Message.error(msg="You are not allowed to do this. Try again.")

            if not user.check_password(current_password):
                return Message.error(
                    msg="Your current password is not correct. Try again."
                )

            user.set_password(new_password)
            user.save()

            reset_password_code.delete()

            return Message.success(msg="Successfully updated the password")

        except Exception as e:
            return Message.error(f"{e}")


class ResetUserEmail(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def create_uid(self):
        uid = tokens.generate_random_code()
        if models.ResetEmailCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.generate_random_code()
        if models.ResetEmailCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            new_email = request.data["email"]

            if models.ResetEmailCode.objects.filter(user=request.user).exists():
                reset_email_code = models.ResetEmailCode.objects.get(user=request.user)

                email.ResetEmailConfirmation(
                    uid=reset_email_code.uid,
                    token=reset_email_code.token,
                    email=new_email,
                    username=request.user.username,
                )

            else:
                uid = self.create_uid()
                token = self.create_token()

                email.ResetEmailConfirmation(
                    uid=uid,
                    token=token,
                    email=new_email,
                    username=request.user.username,
                )
                models.ResetEmailCode.objects.create(
                    user=request.user, uid=uid, token=token, new_email=new_email
                )

            return Message.success(msg="Reset Email link is sent to your email.")

        except Exception as e:
            return Message.error(f"{e}")


class UpdateEmailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            uid = request.data["uid"]
            token = request.data["token"]

            if not models.ResetEmailCode.objects.filter(uid=uid, token=token).exists():
                return Message.error(msg="You have entered wrong code. Try again.")

            reset_email_code = models.ResetEmailCode.objects.filter(
                uid=uid, token=token
            )[0]

            if reset_email_code.user != request.user:
                return Message.error(msg="You are not allowed to do this. Try again.")

            user = request.user
            user.email = reset_email_code.new_email
            user.save()

            reset_email_code.delete()

            return Message.success(msg="Successfully updated the email")

        except Exception as e:
            return Message.error(f"{e}")


class github_auth_redirect(views.APIView):
    def get(self, request, format=None):
        state = str(uuid.uuid4())

        cache.set(f"github_oauth_state_{state}", True, timeout=300)

        redirect_uri = settings.GITHUB_REDIRECT_URI
        app_url = settings.BASE_APP_URL

        github_auth_url = (
            f"https://github.com/login/oauth/authorize/?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={app_url + '/' + redirect_uri}&scope=user&state={state}"
        )
        return response.Response({"url": github_auth_url}, status=status.HTTP_200_OK)


class github_authenticate(views.APIView):
    def get(self, request, format=None):
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code:
            return Message.error(msg="Authorization code not provided")
        if not state:
            return Message.error(msg="State parameter is missing")

        if not cache.get(f"github_oauth_state_{state}"):
            return Message.error(msg="Invalid or expired state parameter")

        cache.delete(f"github_oauth_state_{state}")

        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.BASE_APP_URL + "/" + settings.GITHUB_REDIRECT_URI,
        }

        response_github = requests.post(
            "https://github.com/login/oauth/access_token",
            data=data,
            headers={"Accept": "application/json"},
        )
        access_token = response_github.json().get("access_token")

        if access_token:
            user_data = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()

            github_username = user_data.get("login")

            try:
                if User.objects.filter(username=github_username).exists():
                    user = User.objects.get(username=github_username)

                    user_data = serializers.UserSerializer(user).data
                    tokens = get_tokens_for_user(user)

                    return response.Response(
                        {
                            **tokens,
                            "user": user_data,
                        },
                        status=status.HTTP_200_OK,
                    )

                github_email = (
                    user_data.get("email") if user_data.get("email") else None
                )
                first_name = user_data.get("name").split()[0]
                last_name = "".join(user_data.get("name").split()[1:])
                password = user_data.get("node_id")
                image = user_data.get("avatar_url")

                user = User.objects.create_user(
                    email=github_email,
                    username=github_username,
                    first_name=first_name,
                    last_name=last_name,
                    image=image,
                    method="Github",
                    is_active=True,
                )
                user.set_password(password)
                user.save()

                user_data = serializers.UserSerializer(user).data
                tokens = get_tokens_for_user(user)

                return response.Response(
                    {
                        **tokens,
                        "user": user_data,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Message.error(msg=f"{e}")

        else:
            return Message.error(msg="Failed to authenticate with Github")


class google_auth_redirect(views.APIView):
    def get(self, request, format=None):
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        app_url = settings.BASE_APP_URL

        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={
            settings.GOOGLE_CLIENT_ID}&redirect_uri={app_url + '/' + redirect_uri}&scope=email%20profile&response_type=code"
        return response.Response({"url": google_auth_url}, status=status.HTTP_200_OK)


class google_authenticate(views.APIView):
    def get(self, request, format=None):
        code = request.GET.get("code")

        if not code:
            return Message.error(msg="Authorization code not provided")

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.BASE_APP_URL + "/" + settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response_google = requests.post(
            "https://oauth2.googleapis.com/token", data=data
        )
        access_token = response_google.json().get("access_token")

        if access_token:
            user_data = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()

            google_email = user_data.get("email")

            try:
                if User.objects.filter(email=google_email).exists():
                    user = User.objects.get(email=google_email)
                    user_data = serializers.UserSerializer(user).data

                    tokens = get_tokens_for_user(user)

                    return response.Response(
                        {
                            **tokens,
                            "user": user_data,
                        },
                        status=status.HTTP_200_OK,
                    )

                google_username = google_email.split("@")[0]
                first_name = user_data.get("given_name")
                last_name = user_data.get("family_name")
                password = user_data.get("id")
                image = user_data.get("picture")

                user = User.objects.create_user(
                    email=google_email,
                    username=google_username,
                    first_name=first_name,
                    last_name=last_name,
                    image=image,
                    method="Google",
                    is_active=True,
                )
                user.set_password(password)
                user.save()

                user_data = serializers.UserSerializer(user).data
                tokens = get_tokens_for_user(user)

                return response.Response(
                    {
                        **tokens,
                        "user": user_data,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Message.error(msg=f"{e}")

        else:
            return Message.error(msg="Failed to authenticate with Google")


class ListAllUser(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            users = User.objects.all()
            serialized_data = serializers.UserSerializer(users, many=True)
            return response.Response(serialized_data.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Message.error(f"{e}")
