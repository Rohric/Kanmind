from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from board_app.models import Board


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_staff = bool(request.user and request.user.is_staff)
        return is_staff or request.method in SAFE_METHODS


class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method == "DELETE":
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user == obj.user)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admins haben automatisch Zugriff, auch wenn sie keine Member sind
        if request.user and request.user.is_staff:
            return True

        # Dynamisch: Erkennt, ob das Objekt selbst ein Board ist, oder (wie z.B. bei Tasks) ein Board als Feld hat
        board = obj if isinstance(obj, Board) else obj.board

        return board.memberships.filter(user=request.user).exists()


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Dynamisch: Erkennt, ob das Objekt selbst ein Board ist, oder (wie z.B. bei Tasks) ein Board als Feld hat
        board = obj if isinstance(obj, Board) else obj.board

        return board.memberships.filter(user=request.user, role='owner').exists()
