from rest_framework import generics
from board_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer
from rest_framework.permissions import IsAuthenticated
from . permissions import IsMemberOrOwner
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response


class TestApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'message': 'running...'}, status=status.HTTP_200_OK)


class BoardsList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(memberships__user=user).distinct()


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardSerializer
