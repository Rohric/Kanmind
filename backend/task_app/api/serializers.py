from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from task_app.models import Task, Comment
from user_auth_app.api.serializers import SimpleUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    assignee = SimpleUserSerializer(read_only=True)
    reviewer = SimpleUserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )

    board_title = serializers.CharField(source='board.title', read_only=True)

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'board_title', 'title', 'description', 'status', 'priority',
                  'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
                  'due_date', 'comments_count']

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def validate(self, data):
        board = data.get('board')
        if not board and self.instance:
            board = self.instance.board

        request = self.context.get('request')

        if request and board:
            is_member = board.memberships.filter(user=request.user).exists()
            if not (is_member or request.user.is_superuser):
                raise PermissionDenied(
                    "Verboten. Du musst Mitglied des Boards sein, um Tasks zu erstellen oder zu bearbeiten.")

        assignee = data.get('assignee')
        if assignee and board and not (board.memberships.filter(user=assignee).exists() or assignee.is_superuser):
            raise PermissionDenied(
                "Verboten. Der assignee muss Mitglied des Boards sein, zu dem die Task gehört.")

        reviewer = data.get('reviewer')
        if reviewer and board and not (board.memberships.filter(user=reviewer).exists() or reviewer.is_superuser):
            raise PermissionDenied(
                "Verboten. Der reviewer muss Mitglied des Boards sein, zu dem die Task gehört.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creator'] = request.user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def create(self, validated_data):
        request = self.context.get('request')
        view = self.context.get('view')

        task_id = view.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)

        is_member = task.board.memberships.filter(user=request.user).exists()
        if not (is_member or request.user.is_superuser):
            raise PermissionDenied(
                "Verboten. Du musst Mitglied des Boards sein, um hier zu kommentieren.")

        validated_data['user'] = request.user
        validated_data['task'] = task
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')

        if instance.user != request.user and not request.user.is_superuser:
            raise PermissionDenied(
                "Verboten. Du kannst nur deine eigenen Kommentare bearbeiten.")

        return super().update(instance, validated_data)
