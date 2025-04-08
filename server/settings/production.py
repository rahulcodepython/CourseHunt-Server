"""
Production settings for the CourseHunt project.

This module contains the production-specific settings for the Django application.
It includes configurations for security, database, and CORS.
"""

import os  # Importing os for environment variable access

# Import base settings
from .settings import *  # noqa: F403

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG: bool = False  # Explicitly setting DEBUG to False for production

# Allowed hosts for the application
ALLOWED_HOSTS: list[str] = [
    "localhost",  # Localhost for local testing
    "backend",  # Backend service hostname
    "127.0.0.1",  # Loopback address
    "coursehunt.rahulcodepython.tech",  # Production domain
]

# Database configuration
DATABASE_ENGINE: str = "django.db.backends.postgresql"  # Database engine
# Database name from environment variable
DATABASE_NAME: str = os.getenv("DB_NAME", "")
# Database user from environment variable
DATABASE_USER: str = os.getenv("DB_USER", "")
# Database password from environment variable
DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DATABASE_HOST: str = "postgresdb"  # Database host
DATABASE_PORT: str = "5432"  # Database port

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

# CORS configuration for allowed origins
CORS_ALLOWED_ORIGINS: list[str] = [
    "http://localhost",  # Localhost for local testing
    "http://localhost:80",  # Localhost with port 80
    "http://frontend:3000",  # Frontend service hostname
    "http://localhost:3000",  # Localhost with port 3000
    "http://coursehunt.rahulcodepython.tech",  # Production domain (HTTP)
    "https://coursehunt.rahulcodepython.tech",  # Production domain (HTTPS)
]

# Ensure runtime error handling for missing environment variables
if not DATABASE_NAME or not DATABASE_USER or not DATABASE_PASSWORD:
    raise RuntimeError(
        "Database configuration is incomplete. Ensure DB_NAME, DB_USER, and DB_PASSWORD are set in the environment."
    )
