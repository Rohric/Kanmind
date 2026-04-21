from rest_framework.permissions import BasePermission
from task_app.models import Comment


class IsCreatorOrBoardOwnerForDelete(BasePermission):
    """
    Custom permission for DELETE requests on Tasks and Comments.

    Allows deletion only if the user is the creator of the object
    or the owner of the board the object belongs to.
    """

    def has_object_permission(self, request, view, obj):
        """Check if the user has delete permissions for the object."""
        if request.method != 'DELETE':
            return True

        if isinstance(obj, Comment):
            return obj.user == request.user

        board = getattr(obj, 'board', getattr(obj.task, 'board', None))

        is_board_owner = board.memberships.filter(
            user=request.user, role='owner').exists()

        is_creator = False
        creator_attr = getattr(obj, 'creator', getattr(obj, 'user', None))
        if creator_attr:
            is_creator = (creator_attr == request.user)

        return is_board_owner or is_creator
