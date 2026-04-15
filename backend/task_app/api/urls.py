from django.urls import path
from .views import TaskList, TaskDetails, CommentList, TaskAssigned, TaskReviewer

urlpatterns = [
    path('', TaskList.as_view(), name='tasks-list'),
    path('<int:pk>/', TaskDetails.as_view(), name='task-detail'),
    path('<int:pk>/comments', CommentList.as_view(), name='task-detail'),
    path('assigned-to-me/', TaskAssigned.as_view(), name='tasks-assigned'),
    path('reviewing/', TaskReviewer.as_view(), name='tasks-revierwer'),
]
