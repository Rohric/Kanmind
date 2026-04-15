from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from task_app.models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
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


class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        user = self.request.user

        if user.is_staff:
            return Comment.objects.filter(task_id=task_id)

        # Filtere Kommentare basierend auf der Task-ID und der Board-Mitgliedschaft des Users
        return Comment.objects.filter(
            task_id=task_id,
            task__board__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(Task, id=task_id)
        user = self.request.user

        # Prüfen, ob der User im Board ist (wirft automatisch 403 Forbidden, falls nicht)
        if not user.is_staff and not task.board.memberships.filter(user=user).exists():
            raise PermissionDenied(
                "Der Benutzer muss Mitglied des Boards sein, um einen Kommentar zu erstellen.")

        # Den Kommentar dem User und der Task zuordnen und speichern
        serializer.save(user=user, task=task)
