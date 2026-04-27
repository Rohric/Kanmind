from board_app.models import Board
from rest_framework.permissions import BasePermission


class IsMemberOrOwner(BasePermission):
    """
    Custom permission to only allow members or owners of a board to access it.

    Handles different object types (Board, Task, Comment) by traversing
    relationships to find the associated board.

    Provides specific error messages for different permission failures.
    """

    message = "Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein."

    def has_object_permission(self, request, view, obj):
        """Check if the user is a member or owner of the object's board."""
        if request.user and request.user.is_superuser:
            return True

        is_board_obj = isinstance(obj, Board)
        board = None
        if is_board_obj:
            board = obj
        elif hasattr(obj, "board"):
            board = obj.board
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board

        if not board:
            return False

        if is_board_obj and request.method == "DELETE":
            self.message = "Verboten. Der Benutzer muss der Eigentümer des Boards sein, um es zu löschen."
            return board.memberships.filter(user=request.user, role="owner").exists()

        self.message = "Der Benutzer muss Mitglied eines der Boards oder der Eigentümer eines Boards sein, um es anzuzeigen."
        return board.memberships.filter(user=request.user).exists()
