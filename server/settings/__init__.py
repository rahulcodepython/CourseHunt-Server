"""
This module loads environment-specific settings for the Django application.
It uses the `dotenv` library to load environment variables and dynamically imports
the appropriate settings module based on the `ENVIRONMENT` variable.
"""

# Library to load environment variables from a .env file
from dotenv import load_dotenv
import os  # Standard library for interacting with the operating system

# Load environment variables from the .env file
load_dotenv()

# Get the environment type from the environment variables, defaulting to "local"
environment: str = os.getenv("ENVIRONMENT", "local")

try:
    # Dynamically import settings based on the environment
    if environment == "production":
        from .production import *  # Import production settings
    else:
        from .local import *  # Import local settings
except ImportError as e:
    # Handle import errors gracefully and provide debugging information
    raise ImportError(
        f"Error importing settings for environment '{environment}': {e}")
