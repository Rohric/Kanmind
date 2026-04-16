from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Prüft, ob der anfragende User der eingetragene Assignee DIESES EINEN Tasks ist
        return obj.assignee == request.user


class IsReviewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Prüft, ob der anfragende User der eingetragene Reviewer DIESES EINEN Tasks ist
        return obj.reviewer == request.user


class IsCreatorOrBoardOwnerForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Für alle anderen Methoden (GET, PUT, PATCH) lassen wir die Prüfung durch,
        # da diese durch IsMember geregelt werden.
        if request.method != 'DELETE':
            return True

        # Dynamisch das Board ermitteln (Task hat .board, Comment hat .task.board)
        board = obj.board if hasattr(obj, 'board') else obj.task.board

        # 1. Prüfen, ob der User der Board-Owner ist
        is_board_owner = board.memberships.filter(
            user=request.user, role='owner').exists()

        # 2. Prüfen, ob der User der Ersteller ist (Tasks nutzen 'creator', Comments nutzen 'user')
        is_creator = False
        if hasattr(obj, 'creator'):
            is_creator = (obj.creator == request.user)
        elif hasattr(obj, 'user'):
            is_creator = (obj.user == request.user)

        return is_board_owner or is_creator
