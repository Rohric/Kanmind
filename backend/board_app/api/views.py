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
    message = "Nicht autorisiert. Der Benutzer muss eingeloggt sein."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class TestApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'message': 'running...'}, status=status.HTTP_200_OK)


class BoardsList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [BoardAuthPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(memberships__user=user).distinct()

    def post(self, request, *args, **kwargs):
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
    queryset = Board.objects.all()
    permission_classes = [BoardAuthPermission, IsMemberOrOwner]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=200)
        except Http404:
            return Response(status=404)
        except Exception:
            return Response(status=500)

    def partial_update(self, request, *args, **kwargs):
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
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)
        except Http404:
            return Response(status=404)
        except Exception:
            return Response(status=500)
