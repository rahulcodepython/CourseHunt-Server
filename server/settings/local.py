"""
Local settings for the Django project.
This file contains configurations specific to the local development environment.
"""

import os  # Importing os for environment variable access

# Importing base settings
from .settings import *

# Enable debug mode for local development (Do not use in production)
DEBUG: bool = True

# Allow all hosts for local development (Restrict in production)
ALLOWED_HOSTS: list[str] = ["*"]

# Database configuration for local development
DB_ENGINE: str = "django.db.backends.postgresql"  # Database engine
# Database name with a fallback
DB_NAME: str = os.getenv("DB_NAME", "default_db_name")
# Database user with a fallback
DB_USER: str = os.getenv("DB_USER", "default_user")
# Database password with a fallback
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "default_password")
DB_HOST: str = "postgresdb"  # Database host
DB_PORT: str = "5432"  # Database port

DATABASES: dict[str, dict[str, str]] = {
    "default": {
        "ENGINE": DB_ENGINE,  # Database engine
        "NAME": DB_NAME,  # Database name
        "USER": DB_USER,  # Database user
        "PASSWORD": DB_PASSWORD,  # Database password
        "HOST": DB_HOST,  # Database host
        "PORT": DB_PORT,  # Database port
    },
}

# CORS configuration for local development
CORS_ALLOWED_ORIGINS: list[str] = []  # List of allowed origins (empty for now)
# Allow all origins (not recommended for production)
CORS_ALLOW_ALL_ORIGINS: bool = True
