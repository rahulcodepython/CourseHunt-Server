from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration class for the Authentication application.

    This class defines the basic settings and configurations for the authentication app,
    including database settings and signal handlers.
    """

    # Database configuration for the app
    default_auto_field: str = 'django.db.models.BigAutoField'

    # Application name identifier
    name: str = 'authentication'
