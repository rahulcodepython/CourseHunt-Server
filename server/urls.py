from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import os

environment = os.getenv("ENVIRONMENT", "local")

url_path = "api/" if environment == "production" else ""

urlpatterns = [
    path(url_path, include("server.url_routes")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
