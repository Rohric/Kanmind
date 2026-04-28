from rest_framework.permissions import BasePermission

from task_app.models import Comment, Task


class IsCreatorOrBoardOwnerForDelete(BasePermission):
    """
    Custom permission for DELETE requests on Tasks and Comments.

    Allows deletion only if the user is the creator of the object
    or the owner of the board the object belongs to.
    """

    message = "Verboten. Nur der Ersteller des Objekts oder der Board-Eigentümer kann es löschen."

    def has_object_permission(self, request, view, obj):
        """Check if the user has delete permissions for the object."""
        if request.method != "DELETE":
            return True

        # Determine the board and set the appropriate permission message
        if isinstance(obj, Comment):
            board = obj.task.board
            self.message = "Verboten. Nur der Ersteller des Kommentars oder der Board-Eigentümer kann ihn löschen."
        elif isinstance(obj, Task):
            board = obj.board
            self.message = "Verboten. Nur der Ersteller der Task oder der Board-Eigentümer kann die Task löschen."
        else:
            # Fallback for unexpected object types
            board = getattr(obj, "board", None)

        if not board:
            return False

        is_board_owner = board.memberships.filter(
            user=request.user, role="owner"
        ).exists()
        creator = getattr(obj, "creator", getattr(obj, "user", None))
        is_creator = creator == request.user

        return is_board_owner or is_creator
