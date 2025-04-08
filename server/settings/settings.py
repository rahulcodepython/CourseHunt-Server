"""
Django settings for the CourseHunt project.

This module contains all the configuration settings for the Django project,
including installed apps, middleware, database configurations, authentication,
email setup, and third-party integrations.
"""

from datetime import timedelta
from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Secret key for the project (use environment variable or generate a random one)
SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# Installed applications
INSTALLED_APPS: list[str] = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom apps
    "authentication",
    "course",
    "feedback",
    "transactions",
    "blogs",
    # Third-party packages
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "mail_templated",
]

# Middleware configuration
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root URL configuration
ROOT_URLCONF: str = "server.urls"

# Template configuration
TEMPLATE_DIRS: list[Path] = [BASE_DIR / "templates"]
TEMPLATES: list[dict] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Custom user model
AUTH_USER_MODEL: str = "authentication.User"

# WSGI application
WSGI_APPLICATION: str = "server.wsgi.application"

# Cache configuration
CACHE_BACKEND: str = "django.core.cache.backends.db.DatabaseCache"
CACHE_LOCATION: str = "my_cache_table"
CACHES: dict = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": CACHE_LOCATION,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS: list[dict] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization settings
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "Asia/Kolkata"
USE_I18N: bool = True
USE_TZ: bool = True

# Static files configuration
STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR.parent / "static"

# Default primary key field type
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# Django REST Framework configuration
REST_FRAMEWORK: dict = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# Authentication configuration
AUTH_CONFIG: dict = {"LOGIN_FIELD": "username"}

# Email setup
EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: str = "smtp.gmail.com"
EMAIL_USE_TLS: bool = True
EMAIL_PORT: int = 587
EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
COMPANY_NAME: str = "CourseHunt"

# Process configuration
SEND_ACTIVATION_EMAIL: bool = True
SEND_RESET_PASSWORD_CONFIRMATION_EMAIL: bool = True
SEND_RESET_EMAIL_CONFIRMATION_EMAIL: bool = True
SEND_LOGIN_CONFIRMATION_EMAIL: bool = False
OTP_VERIFICATION_LOGIN: bool = False

# JWT configuration
SIMPLE_JWT: dict = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=4),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "username",
    "USER_ID_CLAIM": "username",
}

# Frontend and backend URLs
BASE_APP_URL: str = os.getenv("BASE_APP_URL", "")
BASE_API_URL: str = os.getenv("BASE_API_URL", "")

# GitHub OAuth details
GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI: str = os.getenv("GITHUB_REDIRECT_URI", "")

# Google OAuth details
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")

# Razorpay configuration
RAZORPAY_API_KEY: str = os.getenv("RAZORPAY_API_KEY", "")
RAZORPAY_SECRET_KEY: str = os.getenv("RAZORPAY_SECRET_KEY", "")
