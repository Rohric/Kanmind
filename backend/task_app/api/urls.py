from django.urls import path
from .views import TaskList, TaskDetails, CommentList, TaskAssigned, TaskReviewer, CommentDetail

urlpatterns = [
    path('', TaskList.as_view(), name='tasks-list'),
    path('<int:pk>/', TaskDetails.as_view(), name='task-detail'),
    path('<int:task_id>/comments/', CommentList.as_view(), name='comment-list'),
    path('<int:task_id>/comments/<int:pk>/',
         CommentDetail.as_view(), name='comment-detail'),
    path('assigned-to-me/', TaskAssigned.as_view(), name='tasks-assigned'),
    path('reviewing/', TaskReviewer.as_view(), name='tasks-revierwer'),
]
