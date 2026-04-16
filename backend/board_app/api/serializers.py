from rest_framework import serializers
from board_app.models import Board, BoardMembership
from task_app.api.serializers import TaskSerializer
from user_auth_app.api.serializers import SimpleUserSerializer


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.SerializerMethodField()
    tasks = TaskSerializer(source='task_set', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_members(self, obj):
        users = [membership.user for membership in obj.memberships.all()]
        serializer = SimpleUserSerializer(
            users, many=True, context=self.context)
        return serializer.data


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

        board = self._create_board(validated_data, user)
        self._handle_members(board, user.id, members)

        return board

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if 'members' in validated_data:
            new_member_ids = set(validated_data.pop('members'))
            owner_id = instance.owner.id

            if owner_id in new_member_ids:
                new_member_ids.remove(owner_id)

            current_member_ids = set(
                BoardMembership.objects.filter(
                    board=instance, role='member').values_list('user_id', flat=True)
            )

            # Mengenlehre: Wer muss gelöscht werden? Wer kommt neu dazu?
            members_to_remove = current_member_ids - new_member_ids
            members_to_add = new_member_ids - current_member_ids

            BoardMembership.objects.filter(
                board=instance, user_id__in=members_to_remove).delete()
            self._add_members(instance, owner_id, members_to_add)

        return instance

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
                    role='member')
