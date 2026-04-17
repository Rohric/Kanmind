from rest_framework import serializers
from board_app.models import Board, BoardMembership
from task_app.api.serializers import TaskSerializer
from user_auth_app.api.serializers import SimpleUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


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

    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    owner_data = SimpleUserSerializer(source='owner', read_only=True)
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', 'owner_id',
                  'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count',
                  'owner_data', 'members_data']

    def get_member_count(self, obj):
        return obj.memberships.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def get_members_data(self, obj):
        users = [membership.user for membership in obj.memberships.all()]
        serializer = SimpleUserSerializer(
            users, many=True, context=self.context)
        return serializer.data

    def validate_members(self, value):
        existing_users = User.objects.filter(
            id__in=value).values_list('id', flat=True)
        if len(existing_users) != len(set(value)):
            raise serializers.ValidationError(
                "Einige der angegebenen Benutzer-IDs existieren nicht.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method in ['PUT', 'PATCH']:
            return {
                'id': data.get('id'),
                'title': data.get('title'),
                'owner_data': data.get('owner_data'),
                'members_data': data.get('members_data')
            }

        data.pop('owner_data', None)
        data.pop('members_data', None)
        return data

    def create(self, validated_data):
        members = validated_data.pop('members')
        user = self.context['request'].user

        board = self.create_board(validated_data, user)
        self.handle_members(board, user.id, members)

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

            members_to_remove = current_member_ids - new_member_ids
            members_to_add = new_member_ids - current_member_ids

            BoardMembership.objects.filter(
                board=instance, user_id__in=members_to_remove).delete()
            self.add_members(instance, owner_id, members_to_add)

        return instance

    def create_board(self, data, user):
        return Board.objects.create(owner=user, **data)

    def handle_members(self, board, owner_id, members):
        self.add_owner(board, owner_id)
        self.add_members(board, owner_id, members)

    def add_owner(self, board, owner_id):
        BoardMembership.objects.create(
            user_id=owner_id,
            board=board,
            role='owner'
        )

    def add_members(self, board, owner_id, members):
        for user_id in set(members):
            if user_id != owner_id:
                BoardMembership.objects.create(
                    user_id=user_id,
                    board=board,
                    role='member')
