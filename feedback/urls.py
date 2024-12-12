from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.CreateFeedback.as_view()),
    path("list/", views.ListFeedback.as_view()),
]
