from rest_framework import serializers
from board_app.models import Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'description', 'owner']
