from django.urls import path
from .views import TaskList, TaskDetails

urlpatterns = [
    path('', TaskList.as_view(), name='tasks-list'),
    path('<int:pk>/', TaskDetails.as_view(),
         name='task-detail'),

]
