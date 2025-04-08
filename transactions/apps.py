from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    """
    Configuration class for the 'transactions' application.
    This class defines application-specific settings and metadata.
    """
    # Setting the default auto field type for models in this app
    default_auto_field: str = 'django.db.models.BigAutoField'

    # Defining the name of the application
    name = 'transactions'
