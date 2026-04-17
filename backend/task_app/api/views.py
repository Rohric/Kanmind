from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from task_app.models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCreatorOrBoardOwnerForDelete
from board_app.api.permissions import IsMemberOrOwner


class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()

        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,
                          IsMemberOrOwner, IsCreatorOrBoardOwnerForDelete]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()

        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskAssigned(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user, board__memberships__user=user).distinct()


class TaskReviewer(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user, board__memberships__user=user).distinct()


class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)

        return Comment.objects.filter(task=task)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,
                          IsMemberOrOwner, IsCreatorOrBoardOwnerForDelete]
