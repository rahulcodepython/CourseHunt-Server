from django.apps import AppConfig  # Importing AppConfig from Django apps module


class CourseConfig(AppConfig):
    """
    Configuration class for the 'course' application.
    This class defines application-specific settings and metadata.
    """
    # Setting the default auto field type for models in this app
    default_auto_field: str = 'django.db.models.BigAutoField'

    # Defining the name of the application
    name = 'course'
