from rest_framework.permissions import BasePermission
from board_app.models import Board


class IsMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        is_board_obj = isinstance(obj, Board)
        board = None
        if is_board_obj:
            board = obj
        elif hasattr(obj, 'board'):  # Handles Task objects
            board = obj.board
        elif hasattr(obj, 'task') and hasattr(obj.task, 'board'):  # Handles Comment objects
            board = obj.task.board

        if not board:
            return False  # Fallback, if no board can be determined

        if is_board_obj and request.method == "DELETE":
            return board.memberships.filter(user=request.user, role='owner').exists()

        return board.memberships.filter(user=request.user).exists()
