from django.urls import path
from .views import TaskList, TaskDetails, CommentList

urlpatterns = [
    path('', TaskList.as_view(), name='tasks-list'),
    path('<int:pk>/', TaskDetails.as_view(),
         name='task-detail'),
    path('<int:pk>/comments', CommentList.as_view(),
         name='task-detail')
]
