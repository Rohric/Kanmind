from rest_framework import generics
from board_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission
from . permissions import IsMemberOrOwner
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404


class BoardAuthPermission(BasePermission):
    """
    Custom permission class to enforce authentication.

    Returns a specific German error message for 401 Unauthorized responses.
    """
    message = "Nicht autorisiert. Der Benutzer muss eingeloggt sein."

    def has_permission(self, request, view):
        """Return `True` if the user is authenticated, `False` otherwise."""
        return bool(request.user and request.user.is_authenticated)


class TestApiView(APIView):
    """A simple view to confirm the API is running."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return a static 'running...' message."""
        return Response({'message': 'running...'}, status=status.HTTP_200_OK)


class BoardsList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating boards.

    - GET: Returns a list of boards the user is a member of.
    - POST: Creates a new board.
    """
    serializer_class = BoardSerializer
    permission_classes = [BoardAuthPermission]

    def get_queryset(self):
        """
        Filter boards to only those the requesting user is a member of.

        Staff users can see all boards.
        """
        user = self.request.user
        if user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(memberships__user=user).distinct()

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to create a new board with custom error handling.

        Returns status 400 for validation errors and 500 for server errors,
        both with empty bodies.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=400)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        except Exception:
            return Response(status=500)


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a single board.

    - GET: Retrieve a board's details.
    - PATCH: Update a board's title and/or members.
    - DELETE: Delete a board.
    """
    queryset = Board.objects.all()
    permission_classes = [BoardAuthPermission, IsMemberOrOwner]

    def get_serializer_class(self):
        """Return `BoardDetailSerializer` for GET, `BoardSerializer` otherwise."""
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request with custom error handling.

        Returns status 404 for not found and 500 for server errors,
        both with empty bodies.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=200)
        except Http404:
            return Response(status=404)
        except Exception:
            return Response(status=500)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH request with custom error handling.

        Returns status 400 for validation errors, 404 for not found,
        and 500 for server errors, all with empty bodies.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(status=400)
            self.perform_update(serializer)
            return Response(serializer.data, status=200)
        except Http404:
            return Response(status=404)
        except Exception:
            return Response(status=500)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request with custom error handling.

        Returns status 204 on success, 404 for not found, and 500 for
        server errors, all with empty bodies.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)
        except Http404:
            return Response(status=404)
        except Exception:
            return Response(status=500)
