from django.conf import settings  # Import Django settings for configuration
# Import Literal for type hints and Optional for nullable types
from typing import Literal, Optional
from django.core.paginator import Page  # Import Page for pagination handling

# Base API URL fetched from Django settings
BASE_API_URL: str = settings.BASE_API_URL


def pagination_next_url_builder(page: Page, url: str) -> Optional[str]:
    """
    Builds the next page URL for pagination if a next page exists.

    Args:
        page (Page): The current page object from Django's paginator.
        url (str): The base URL to append the page query parameter.

    Returns:
        Optional[str]: The next page URL if a next page exists, otherwise None.
    """
    # Check if there is a next page and construct the URL
    if page.has_next():
        next_page_number: int = page.next_page_number()  # Get the next page number
        # Construct the next page URL
        next_url: str = f"{BASE_API_URL}{url}?page={next_page_number}"
        return next_url
    return None  # Return None if no next page exists


def redirect_uri_builder(purpose: Literal["github", "google"]) -> str:
    """
    Builds the redirect URI for OAuth purposes based on the provider.

    Args:
        purpose (Literal["github", "google"]): The purpose of the redirect URI, either 'github' or 'google'.

    Returns:
        str: The constructed redirect URI.
    """
    # Base app URL fetched from Django settings
    base_app_url: str = settings.BASE_APP_URL

    # Construct the redirect URI based on the purpose
    if purpose == "github":
        # Fetch GitHub redirect URI from settings
        github_redirect_uri: str = settings.GITHUB_REDIRECT_URI
        return f"{base_app_url}/{github_redirect_uri}"
    elif purpose == "google":
        # Fetch Google redirect URI from settings
        google_redirect_uri: str = settings.GOOGLE_REDIRECT_URI
        return f"{base_app_url}/{google_redirect_uri}"
    else:
        # Raise error for invalid input
        raise ValueError("Invalid purpose provided. Use 'github' or 'google'.")
