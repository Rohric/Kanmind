from rest_framework import generics
from board_app.models import Board
from .serializers import BoardSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from . permissions import IsAdminForDeleteOrPatchAndReadOnly


class BoardsList(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsAdminForDeleteOrPatchAndReadOnly]
