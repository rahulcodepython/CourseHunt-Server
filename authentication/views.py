from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from rest_framework import views, response, status
from django.conf import settings
from . import serializers, email, models, tokens
import requests

User = get_user_model()


class Message:
    def warn(msg: str) -> object:
        return {"body": {"warn": msg}, "status": status.HTTP_406_NOT_ACCEPTABLE}

    def error(msg: str) -> object:
        return {"body": {"error": msg}, "status": status.HTTP_400_BAD_REQUEST}

    def success(msg: str) -> object:
        return {"body": {"success": msg}, "status": status.HTTP_200_OK}

    def create(msg: str) -> object:
        return {"body": {"success": msg}, "status": status.HTTP_201_CREATED}


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


class UserViews(views.APIView):
    def create_uid(self) -> int:
        uid: int = tokens.create_uid()
        if models.ActivationCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self) -> int:
        token: int = tokens.create_token()
        if models.ActivationCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    @staticmethod
    def generate_unique_username(email: str) -> str:
        return email.split('@')[0]

    def get(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            serialized_data = serializers.UserSerializer(request.user)
            return response.Response(serialized_data.data, status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])

    def post(self, request):
        try:
            if check_email_exists(request.data["email"]):
                if not check_user_active(request.data["email"]):
                    res = Message.warn(
                        msg="You have already registered. But not verified you email yet. Please verify it first.")
                    return response.Response(res["body"], status=res["status"])

                res = Message.warn(msg="You have already registered.")
                return response.Response(res["body"], status=res["status"])

            serialized_data = serializers.UserCreateSerializer(
                data={**request.data, "username": self.generate_unique_username(request.data["email"])})

            if not serialized_data.is_valid():
                res = Message.error(
                    "There is some issue. User is not created. Try again."
                )
                return response.Response(res["body"], status=res["status"])

            user = serialized_data.save()

            activation_code = models.ActivationCode.objects.create(
                user=user, uid=self.create_uid(), token=self.create_token()
            )
            email.ActivationEmail(uid=activation_code.uid, token=activation_code.token, email=user.email,
                                  username=user.username)

            res = Message.create(msg="Your account has been creates. At First verify it.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])

    def patch(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            serialized_data = serializers.UserUpdateSerializer(
                request.user, data=request.data, partial=True
            )

            if not serialized_data.is_valid():
                res = Message.error(msg="Your data is not valid. Try again.")
                return response.Response(res["body"], status=res["status"])

            serialized_data.save()

            res = Message.create(msg="Your data is updated.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])

    def delete(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            request.user.delete()
            res = Message.success(msg="Your account is deleted.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


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
                res = Message.error(msg="You have entered wrong code. Try again.")
                return response.Response(res["body"], status=res["status"])

            user.is_active = True
            user.save()
            models.ActivationCode.objects.filter(uid=uid, token=token)[0].delete()

            return response.Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class ResendActivateUserViews(views.APIView):
    def create_uid(self):
        uid = tokens.create_uid()
        if models.ActivationCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.create_token()
        if models.ActivationCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            user_email = request.data["email"]

            if not check_email_exists(user_email):
                res = Message.error(msg="No such user is there. Try again.")
                return response.Response(res["body"], status=res["status"])

            user = User.objects.get(email=user_email)

            if check_user_active(user_email):
                res = Message.error(msg="You are already verified.")
                return response.Response(res["body"], status=res["status"])

            if models.ActivationCode.objects.filter(user=user).exists():
                models.ActivationCode.objects.get(user=user).delete()

            activation_code = models.ActivationCode.objects.create(
                user=user, uid=self.create_uid(), token=self.create_token()
            )

            email.ActivationEmail(uid=activation_code.uid, token=activation_code.token, email=user.email,
                                  username=user.username)

            res = Message.success(msg="Activation link has been sent to your email.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class CreateJWT(views.APIView):
    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]

            if not User.objects.filter(email=email).exists():
                res = Message.error(msg="No such user is there. Try again.")
                return response.Response(res["body"], status=res["status"])

            username = User.objects.get(email=email).username

            user = authenticate(username=username, password=password)

            if user is None:
                res = Message.error(msg="You are not authenticated properly. Try again.")
                return response.Response(res["body"], status=res["status"])

            if not user.is_active:
                res = Message.error(msg="You are not verified yet. Verify first.")
                return response.Response(res["body"], status=res["status"])

            res = Message.success(msg="You are authenticated.")
            return response.Response(
                {**res["body"], **get_tokens_for_user(user)}, status=res["status"]
            )

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class ResetUserPassword(views.APIView):
    def create_uid(self):
        uid = tokens.create_uid()
        if models.ResetPasswordCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.create_token()
        if models.ResetPasswordCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def get(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            if models.ResetPasswordCode.objects.filter(user=request.user).exists():
                models.ResetPasswordCode.objects.get(user=request.user).delete()

            reset_password_code = models.ResetPasswordCode.objects.create(
                user=request.user, uid=self.create_uid(), token=self.create_token()
            )
            email.ResetPasswordConfirmation(uid=reset_password_code.uid, token=reset_password_code.token,
                                            email=request.user.email, username=request.user.username)

            res = Message.success(msg="Reset Password link is sent to your mail.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])

    def post(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            new_password = request.data["new_password"]
            current_password = request.data["current_password"]
            uid = request.data["uid"]
            token = request.data["token"]

            if not models.ResetPasswordCode.objects.filter(uid=uid, token=token).exists():
                res = Message.error(msg="You have entered wrong code. Try again.")
                return response.Response(res["body"], status=res["status"])

            reset_password_code = models.ResetPasswordCode.objects.filter(uid=uid, token=token)[0]

            if reset_password_code.user != request.user:
                res = Message.error(msg="You are not allowed to do this. Try again.")
                return response.Response(res["body"], status=res["status"])

            user = request.user

            if not user.check_password(current_password):
                res = Message.error(msg="Your current password is not correct. Try again.")
                return response.Response(res["body"], status=res["status"])

            user.set_password(new_password)
            user.save()

            reset_password_code.delete()

            res = Message.success(msg="Successfully changed the password")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class ResetUserEmail(views.APIView):
    def create_uid(self):
        uid = tokens.create_uid()
        if models.ResetEmailCode.objects.filter(uid=uid).exists():
            self.create_uid()
        return uid

    def create_token(self):
        token = tokens.create_token()
        if models.ResetEmailCode.objects.filter(token=token).exists():
            self.create_token()
        return token

    def post(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            new_email = request.data["email"]

            if models.ResetEmailCode.objects.filter(user=request.user).exists():
                models.ResetEmailCode.objects.get(user=request.user).delete()

            reset_email_code = models.ResetEmailCode.objects.create(
                user=request.user, uid=self.create_uid(), token=self.create_token()
            )
            email.ResetEmailConfirmation(uid=reset_email_code.uid, token=reset_email_code.token,
                                         email=new_email, username=request.user.username)

            res = Message.success(msg="Reset Email link is sent to your email.")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class UpdateEmailView(views.APIView):
    def post(self, request):
        try:
            if not check_authenticated_user(request.user):
                res = Message.error(msg="You are not authenticated yet. Try again.")
                return response.Response(res["body"], status=res["status"])

            new_email = request.data["email"]
            uid = request.data["uid"]
            token = request.data["token"]

            if not models.ResetEmailCode.objects.filter(uid=uid, token=token).exists():
                res = Message.error(msg="You have entered wrong code. Try again.")
                return response.Response(res["body"], status=res["status"])

            reset_email_code = models.ResetEmailCode.objects.filter(uid=uid, token=token)[0]

            if reset_email_code.user != request.user:
                res = Message.error(msg="You are not allowed to do this. Try again.")
                return response.Response(res["body"], status=res["status"])

            user = request.user
            user.email = new_email
            user.save()

            reset_email_code.delete()

            res = Message.success(msg="Successfully updated the email")
            return response.Response(res["body"], status=res["status"])

        except Exception as e:
            res = Message.error(f"{e}")
            return response.Response(res["body"], status=res["status"])


class github_auth_redirect(views.APIView):
    def get(self, request, format=None):
        redirect_uri = settings.GITHUB_REDIRECT_URI
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}&scope=user"
        return response.Response({"url": github_auth_url}, status=status.HTTP_200_OK)


class github_authenticate(views.APIView):
    def get(self, request, format=None):
        code = request.GET.get("code")
        if not code:
            return response.Response(
                {"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
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
                headers={"Authorization": f"token {access_token}"},
            ).json()

            github_username = user_data.get("login")

            try:
                if User.objects.filter(username=github_username).exists():
                    user = User.objects.get(username=github_username)
                    return response.Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

                github_email = user_data.get("email") if user_data.get("email") else None
                first_name = user_data.get("name").split()[0]
                last_name = ''.join(user_data.get("name").split()[1:])
                password = user_data.get("node_id")
                image = user_data.get("avatar_url")
                # html_url = user_data.get("html_url")
                # bio = user_data.get("bio")

                user = User.objects.create_user(
                    email=github_email,
                    username=github_username,
                    first_name=first_name,
                    last_name=last_name,
                    image=image,
                    method='Github',
                    is_active=True
                )
                user.set_password(password)
                user.save()

                return response.Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
                # return response.Response({"error": str("e")}, status=status.HTTP_200_OK)

            except Exception as e:
                return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return response.Response(
                {"error": "Failed to authenticate with GitHub"}, status=status.HTTP_400_BAD_REQUEST
            )


class google_auth_redirect(views.APIView):
    def get(self, request, format=None):
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=email%20profile&response_type=code"
        return response.Response({"url": google_auth_url}, status=status.HTTP_200_OK)


class google_authenticate(views.APIView):
    def get(self, request, format=None):
        code = request.GET.get("code")
        if not code:
            return response.Response(
                {"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response_google = requests.post("https://oauth2.googleapis.com/token", data=data)
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
                    return response.Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

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
                    method='Google',
                    is_active=True
                )
                user.set_password(password)
                user.save()

                return response.Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

            except Exception as e:
                return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return response.Response(
                {"error": "Failed to authenticate with Google"}, status=status.HTTP_400_BAD_REQUEST
            )