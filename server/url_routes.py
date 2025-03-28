from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.Test.as_view()),
    path("auth/", include("authentication.urls")),
    path("course/", include("course.urls")),
    path("feedback/", include("feedback.urls")),
    path("transactions/", include("transactions.urls")),
    path("blogs/", include("blogs.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
