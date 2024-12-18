from django.conf import settings
from typing import Literal
from django.core.paginator import Page

BASE_API_URL = settings.BASE_API_URL


def pagination_next_url_builder(page: Page, url: str) -> str | None:
    return (
        f"{BASE_API_URL}/{url}?page={page.next_page_number()}"
        if page.has_next()
        else None
    )


def redirect_uri_builder(purpose: Literal["github", "google"]) -> str:
    if purpose == "github":
        return f"{settings.BASE_APP_URL}/{settings.GITHUB_REDIRECT_URI}"
    elif purpose == "google":
        return f"{settings.BASE_APP_URL}/{settings.GOOGLE_REDIRECT_URI}"
