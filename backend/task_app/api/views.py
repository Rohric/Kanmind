from rest_framework import generics
from task_app.models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Wenn der User ein Admin ist, zeige ihm alle Tasks
        if user.is_staff:
            return Task.objects.all()

        # Ansonsten filtere nach Tasks, deren Board-Mitglied der User ist
        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Wenn der User ein Admin ist, zeige ihm alle Tasks
        if user.is_staff:
            return Task.objects.all()

        # Ansonsten filtere nach Tasks, deren Board-Mitglied der User ist
        return Task.objects.filter(board__memberships__user=user).distinct()
