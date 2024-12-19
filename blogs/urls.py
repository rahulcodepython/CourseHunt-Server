from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.ListAllBlogsView.as_view()),
    # path("create/", views.CreateBlog.as_view()),
    # path("update/<int:pk>/", views.UpdateBlog.as_view()),
    # path("read/<int:pk>/", views.ReadBlog.as_view()),
    # path("create-comment/", views.CreateComment.as_view()),
    # path("update-comment/<int:pk>/", views.UpdateComment.as_view()),
    # path("like-blog/<int:pk>/", views.LikeBlog.as_view()),
]
