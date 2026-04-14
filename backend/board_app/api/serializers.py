from rest_framework import serializers
from board_app.models import Board, BoardMembership


# class BoardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Board
#         fields = ['name', 'description', 'owner']


class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    member_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', 'owner_id']

    def get_member_count(self, obj):
        return obj.memberships.count()

    def create(self, validated_data):
        members = validated_data.pop('members')
        user = self.context['request'].user

        board = Board.objects.create(owner=user, **validated_data)

        BoardMembership.objects.create(
            user=user,
            board=board,
            role='owner'
        )

        for user_id in members:
            if user_id != user.id:
                BoardMembership.objects.create(
                    user_id=user_id,
                    board=board,
                    role='editor'
                )

        return board
