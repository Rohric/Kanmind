from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from board_app.api.permissions import IsMemberOrOwner
from board_app.api.views import BoardAuthPermission
from board_app.models import Board
from task_app.models import Comment, Task

from .permissions import IsCreatorOrBoardOwnerForDelete
from .serializers import CommentSerializer, TaskSerializer


class TaskList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating tasks.

    - GET: Returns a list of tasks from boards the user is a member of.
    - POST: Creates a new task within a board.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(board__memberships__user=user).distinct()

    def create(self, request, *args, **kwargs):

        board_id = request.data.get("board")

        if board_id:
            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return Response(
                    {
                        "error": "Board nicht gefunden. Die angegebene Board-ID existiert nicht."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            is_member = board.memberships.filter(user=request.user).exists()
            if not is_member and not request.user.is_staff:
                return Response(
                    {
                        "error": "Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return super().create(request, *args, **kwargs)


class TaskDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a single task.

    Permissions are checked to ensure the user is a member of the board.
    Deletion is restricted to the task creator or board owner.
    """

    serializer_class = TaskSerializer
    permission_classes = [
        BoardAuthPermission,
        IsMemberOrOwner,
        IsCreatorOrBoardOwnerForDelete,
    ]

    def get_queryset(self):
        return Task.objects.all()

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request with custom error handling.

        Returns status 204 on success, 404 for not found, and 500 for
        server errors, all with empty bodies. Permission errors (403)
        are handled by DRF and include a message.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            raise
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskAssigned(generics.ListAPIView):
    """API endpoint to list all tasks assigned to the current user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """Return tasks where the current user is the assignee."""
        user = self.request.user
        return Task.objects.filter(
            assignee=user, board__memberships__user=user
        ).distinct()


class TaskReviewer(generics.ListAPIView):
    """API endpoint to list all tasks where the current user is the reviewer."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        """Return tasks where the current user is the reviewer."""
        user = self.request.user
        return Task.objects.filter(
            reviewer=user, board__memberships__user=user
        ).distinct()


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
        task_id = self.kwargs.get("task_id")
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
    permission_classes = [
        IsAuthenticated,
        IsMemberOrOwner,
        IsCreatorOrBoardOwnerForDelete,
    ]
