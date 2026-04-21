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
    """
    API endpoint for listing and creating tasks.

    - GET: Returns a list of tasks from boards the user is a member of.
    - POST: Creates a new task within a board.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """Filter tasks to only those on boards the user is a member of."""
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()

        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a single task.

    Permissions are checked to ensure the user is a member of the board.
    Deletion is restricted to the task creator or board owner.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,
                          IsMemberOrOwner, IsCreatorOrBoardOwnerForDelete]

    def get_queryset(self):
        """Filter tasks to only those on boards the user is a member of."""
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()

        return Task.objects.filter(board__memberships__user=user).distinct()


class TaskAssigned(generics.ListAPIView):
    """API endpoint to list all tasks assigned to the current user."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """Return tasks where the current user is the assignee."""
        user = self.request.user
        return Task.objects.filter(assignee=user, board__memberships__user=user).distinct()


class TaskReviewer(generics.ListAPIView):
    """API endpoint to list all tasks where the current user is the reviewer."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """Return tasks where the current user is the reviewer."""
        user = self.request.user
        return Task.objects.filter(reviewer=user, board__memberships__user=user).distinct()


class CommentList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating comments for a specific task.

    The task is identified by `task_id` in the URL.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """
        Return comments for the specified task.

        Also checks object-level permissions to ensure the user can view the task.
        """
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, task)

        return Comment.objects.filter(task=task)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a single comment.

    Deletion is restricted to the comment creator or board owner.
    Updating is restricted to the comment creator.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,
                          IsMemberOrOwner, IsCreatorOrBoardOwnerForDelete]
