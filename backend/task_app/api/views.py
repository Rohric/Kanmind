from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from task_app.models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsAdmin
from board_app.api.permissions import IsMember


class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def get_queryset(self):
        user = self.request.user
        # Wenn der User ein Admin ist, zeige ihm alle Tasks
        if user.is_staff:
            return Task.objects.all()

        # Ansonsten filtere nach Tasks, deren Board-Mitglied der User ist
        return Task.objects.filter(board__memberships__user=user).distinct()

    def perform_create(self, serializer):
        # 1. Das Ziel-Board aus den validierten Daten des Requests holen
        board = serializer.validated_data['board']
        # 2. Unsere Permission (IsMember) zwingen, dieses Board zu prüfen (Wirft 403, wenn nicht drin!)
        self.check_object_permissions(self.request, board)
        # 3. Wenn kein Fehler geworfen wurde, den Task speichern
        serializer.save()


class TaskDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember, IsAdmin]

    def get_queryset(self):
        user = self.request.user

        # Wenn der User ein Admin ist, zeige ihm alle Tasks
        if user.is_staff:
            return Task.objects.all()

        # Ansonsten filtere nach Tasks, deren Board-Mitglied der User ist
        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskAssigned(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember, IsAdmin]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(assignee=user) | Q(reviewer=user)).distinct()


class TaskReviewer(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMember, IsAdmin]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(reviewer=user)).distinct()


class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsMember, IsAdmin]

    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        # Wirft 404, wenn Task fehlt
        task = get_object_or_404(Task, id=task_id)

        # Triggert IsMember. Wirft automatisch 403, wenn der User kein Member ist!
        self.check_object_permissions(self.request, task)

        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(Task, id=task_id)

        # Triggert IsMember auch beim Erstellen eines neuen Kommentars!
        self.check_object_permissions(self.request, task)

        # Den Kommentar dem User und der Task zuordnen und speichern
        serializer.save(user=self.request.user, task=task)
