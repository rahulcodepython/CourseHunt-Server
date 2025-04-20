from django.urls import path
from . import views

urlpatterns = [
    # Course management
    path('list/all-courses/', views.CourseListForAllUsers.as_view(), name='course-list-all-courses-for-all-users'),
    path('detail/<pk>/', views.CourseDetailForAllUsers.as_view(), name='course-detail-all-courses-for-all-users'),
    # path('create/', views.CourseCreate.as_view(), name='course-create'),
    # path('manage/<pk>/',
    #      views.CourseUpdateDestroy.as_view(), name='course-manage'),
    # path('purchase/', views.PurchaseCourse.as_view(), name='purchase-course'),
    # path('my-courses/', views.UserCoursesList.as_view(), name='user-courses'),
    # path('complete-lecture/', views.CompleteLecture.as_view(),
    #      name='complete-lecture'),
]