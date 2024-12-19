from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.ListAllBlogsView.as_view()),
    path("list-admin/", views.AdminListAllBlogsView.as_view()),
    path("read/<str:blog_id>/", views.ReadBlogView.as_view()),
    path("create-comment/", views.CreateCommentView.as_view()),
    path("like-blog/<str:blog_id>/", views.LikeBlogView.as_view()),
    path("create/", views.CreateBlogView.as_view()),
    path("update/<str:blog_id>/", views.UpdateBlogView.as_view()),
    path("edit-comment/<str:comment_id>/", views.UpdateComment.as_view()),
]
