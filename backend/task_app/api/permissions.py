from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


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
        return bool(request.user and request.user.is_staff)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
