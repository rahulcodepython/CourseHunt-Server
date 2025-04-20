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

# Environment mode (development or production)
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
DEVELOPMENT: bool = ENVIRONMENT == "development"

# Debug mode (set to False in production)
DEBUG: bool = DEVELOPMENT

# Allowed hosts for the application
ALLOWED_HOSTS_ENV: str = os.getenv(
    "ALLOWED_HOSTS", "0.0.0.0,127.0.0.1,localhost"
)
ALLOWED_HOSTS: list[str] = (
    ALLOWED_HOSTS_ENV.split(",") if not DEVELOPMENT else ["*"]
)

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
    "instructor",
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

# Database configuration
DATABASE_ENGINE: str = "django.db.backends.postgresql"  # Database engine
# Database name from environment variable
DATABASE_NAME: str = os.getenv("DB_NAME", "")
# Database user from environment variable
DATABASE_USER: str = os.getenv("DB_USER", "")
# Database password from environment variable
DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DATABASE_HOST: str = os.getenv("DB_HOST", "")  # Database host
DATABASE_PORT: str = os.getenv("DB_PORT", "")  # Database port

# Setting up the DATABASES dictionary
DATABASES: dict[str, dict[str, str]] = {
    "default": {
        "ENGINE": DATABASE_ENGINE,  # Database engine
        "NAME": DATABASE_NAME,  # Database name
        "USER": DATABASE_USER,  # Database user
        "PASSWORD": DATABASE_PASSWORD,  # Database password
        "HOST": DATABASE_HOST,  # Database host
        "PORT": DATABASE_PORT,  # Database port
    }
}

# Template configuration
TEMPLATE_DIRS: list[Path] = []
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

# Default primary key field type
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# Django REST Framework configuration
REST_FRAMEWORK: dict = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.authentication.CookieJWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# Cors configuration
CORS_ALLOW_ALL_ORIGINS: bool = DEVELOPMENT
CORS_ALLOWED_ORIGINS: list[str] = os.getenv(
    "CORS_ALLOWED_ORIGINS", "").split(",") if not DEVELOPMENT else []

# Authentication configuration
AUTH_CONFIG: dict = {"LOGIN_FIELD": "username"}

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
    "AUTH_COOKIE_SECURE": True,
    "AUTH_COOKIE_SAMESITE": "Lax",
    "AUTH_COOKIE_HTTP_ONLY": True,
}

# CONSTANTS
SITE_NAME: str = "CourseHunt"
