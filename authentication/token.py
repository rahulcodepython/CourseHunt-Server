from typing import TypedDict
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
# Assuming User model is defined in authentication.models
from authentication.models import User


class TokenDict(TypedDict):
    """Type definition for JWT token response"""
    refresh: str
    access: str


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
