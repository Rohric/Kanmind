from rest_framework import generics
from board_app.models import Board
from .serializers import BoardSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from . permissions import IsAdminForDeleteOrPatchAndReadOnly, IsMember, IsBoardOwner, IsOwnerOrAdmin
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response


class TestApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'message': 'running...'}, status=status.HTTP_200_OK)


class BoardsList(generics.ListCreateAPIView):
    # queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsMember, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # Wenn der User ein Admin ist, zeige ihm alle Tasks
        if user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(memberships__user=user).distinct()


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsMember, IsBoardOwner]
