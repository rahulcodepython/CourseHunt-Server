from django.urls import path
from . import views

urlpatterns =[
    path('member/<user>/', views.InstructorDetailView.as_view(), name='instructor'),
    path('list/', views.InstructorListView.as_view(), name='instructor-list'),
    path('join-instructor/', views.JoinInstructorView.as_view(), name='join-instructor'),
]