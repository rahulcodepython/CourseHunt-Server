from typing import TypedDict
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models


class TokenDict(TypedDict):
    """Type definition for JWT token response"""
    refresh: str
    access: str


# Get User model at module level
User = get_user_model()


def GenerateToken(user: models.User) -> TokenDict:
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
