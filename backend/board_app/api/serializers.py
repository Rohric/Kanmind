from rest_framework import serializers
from board_app.models import Board, BoardMembership


# class BoardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Board
#         fields = ['name', 'description', 'owner']


class BoardMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMembership
        fields = ['user', 'board', 'role']


class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    member_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, obj):
        return obj.memberships.count()

    def create(self, validated_data):
        members = validated_data.pop('members')
        user = self.context['request'].user

        board = self._create_board(validated_data, user)
        self._handle_members(board, user.id, members)

        return board

    def _create_board(self, data, user):
        return Board.objects.create(owner=user, **data)

    def _handle_members(self, board, owner_id, members):
        self._add_owner(board, owner_id)
        self._add_members(board, owner_id, members)

    def _add_owner(self, board, owner_id):
        BoardMembership.objects.create(
            user_id=owner_id,
            board=board,
            role='owner'
        )

    def _add_members(self, board, owner_id, members):
        for user_id in set(members):
            if user_id != owner_id:
                BoardMembership.objects.create(
                    user_id=user_id,
                    board=board,
                    role='member'
                )

    def get_ticket_count(self, obj):
        return 0

    def get_tasks_to_do_count(self, obj):
        return 0

    def get_tasks_high_prio_count(self, obj):
        return 0
