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


class IsTaskCreatorOrBoardOwnerForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Für alle anderen Methoden (GET, PUT, PATCH) lassen wir die Prüfung durch,
        # da diese durch IsMember geregelt werden.
        if request.method != 'DELETE':
            return True

        # 1. Prüfen, ob der User der Board-Owner ist
        is_board_owner = obj.board.memberships.filter(
            user=request.user, role='owner').exists()

        # 2. Prüfen, ob der User der Ersteller des Tasks ist
        is_creator = hasattr(obj, 'creator') and obj.creator == request.user

        return is_board_owner or is_creator
