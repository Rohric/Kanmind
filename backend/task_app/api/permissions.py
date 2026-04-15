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
