from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost", "backend", "127.0.0.1"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv(
            "DB_NAME",
        ),
        "USER": os.getenv(
            "DB_USER",
        ),
        "PASSWORD": os.getenv(
            "DB_PASSWORD",
        ),
        "HOST": "db",
        "PORT": "5432",
    }
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = ["http://localhost", "http://localhost:80"]

SEND_LOGIN_CONFIRMATION_EMAIL = not DEBUG

OTP_VERIFICATION_LOGIN = not DEBUG
