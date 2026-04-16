from rest_framework.permissions import BasePermission


class IsCreatorOrBoardOwnerForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True

        board = obj.board if hasattr(obj, 'board') else obj.task.board

        is_board_owner = board.memberships.filter(
            user=request.user, role='owner').exists()

        is_creator = False
        if hasattr(obj, 'creator'):
            is_creator = (obj.creator == request.user)
        elif hasattr(obj, 'user'):
            is_creator = (obj.user == request.user)

        return is_board_owner or is_creator
