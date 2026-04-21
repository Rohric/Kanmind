from rest_framework import serializers
from board_app.models import Board, BoardMembership
from task_app.api.serializers import NestedTaskSerializer
from user_auth_app.api.serializers import SimpleUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the detailed view of a Board.

    Includes nested serialization for associated members and tasks.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.SerializerMethodField()
    tasks = NestedTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_members(self, obj):
        """Return a serialized list of all board members."""
        memberships = obj.memberships.select_related('user').all()
        users = [membership.user for membership in memberships]
        serializer = SimpleUserSerializer(
            users, many=True, context=self.context)
        return serializer.data


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for listing, creating, and updating Boards.

    - Handles creation and updates with a list of member IDs.
    - Provides aggregated data like member and task counts for list views.
    - Customizes representation for list vs. update views.
    """
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
        """Return the total number of members in the board."""
        return obj.memberships.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks in the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status 'to-do'."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with priority 'high'."""
        return obj.tasks.filter(priority='high').count()

    def get_members_data(self, obj):
        """Return a serialized list of all board members."""
        memberships = obj.memberships.select_related('user').all()
        users = [membership.user for membership in memberships]
        serializer = SimpleUserSerializer(
            users, many=True, context=self.context)
        return serializer.data

    def validate_members(self, value):
        """Ensure all provided member IDs correspond to existing users."""
        existing_users = User.objects.filter(
            id__in=value).values_list('id', flat=True)
        if len(existing_users) != len(set(value)):
            raise serializers.ValidationError(
                "Einige der angegebenen Benutzer-IDs existieren nicht.")
        return value

    def to_representation(self, instance):
        """
        Customize the serialized output.

        - For PUT/PATCH, return a simple representation with member details.
        - For GET (list), return the full representation with counts.
        """
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
        """
        Create a new Board and its memberships.

        The requesting user becomes the owner. Other users from the 'members'
        list are added as members.
        """
        member_ids = set(validated_data.pop('members'))
        user = self.context['request'].user

        board = Board.objects.create(owner=user, **validated_data)

        memberships_to_create = [
            BoardMembership(user=user, board=board, role='owner')
        ]
        for user_id in member_ids:
            if user_id != user.id:
                memberships_to_create.append(
                    BoardMembership(user_id=user_id,
                                    board=board, role='member')
                )
        BoardMembership.objects.bulk_create(memberships_to_create)

        return board

    def update(self, instance, validated_data):
        """
        Update a Board's title and its members.

        Compares the new list of member IDs with the existing ones to add
        or remove memberships as needed. The owner cannot be removed.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if 'members' in validated_data:
            new_member_ids = set(validated_data.get('members'))
            owner_id = instance.owner.id

            if owner_id in new_member_ids:
                new_member_ids.remove(owner_id)

            current_member_ids = set(
                BoardMembership.objects.filter(
                    board=instance, role='member').values_list('user_id', flat=True)
            )

            members_to_remove = current_member_ids - new_member_ids
            members_to_add = new_member_ids - current_member_ids

            if members_to_remove:
                BoardMembership.objects.filter(
                    board=instance, user_id__in=members_to_remove).delete()
            if members_to_add:
                new_memberships = [
                    BoardMembership(user_id=user_id,
                                    board=instance, role='member')
                    for user_id in members_to_add
                ]
                BoardMembership.objects.bulk_create(new_memberships)

        return instance
