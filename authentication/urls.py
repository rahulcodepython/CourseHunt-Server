from typing import List
from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

# Combine all URL patterns
urlpatterns: List[URLPattern] = [
    path("users/jwt/create/", views.CreateJWTView.as_view(), name="token_create"),
]
