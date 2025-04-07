from typing import ClassVar
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration class for the Authentication application.

    This class defines the basic settings and configurations for the authentication app,
    including database settings and signal handlers.
    """

    # Database configuration for the app
    default_auto_field: ClassVar[str] = 'django.db.models.BigAutoField'

    # Application name identifier
    name: ClassVar[str] = 'authentication'

    def ready(self) -> None:
        """
        Perform initialization tasks when the application is ready.
        This method is called by Django when the application is starting.
        """
        # Import signals to ensure they are registered
        from . import signals  # noqa
