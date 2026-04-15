from rest_framework import serializers
from task_app.models import Task, Comment
from user_auth_app.api.serializers import SimpleUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    # Für die Antwort (Read-Only): Wir nutzen den neuen Serializer für die verschachtelte Darstellung
    assignee = SimpleUserSerializer(read_only=True)
    reviewer = SimpleUserSerializer(read_only=True)

    # Für den Request (Write-Only): Wir akzeptieren die IDs, so wie im Postman-Body verlangt
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
        # Greift auf die 'comment_set' Relation zu, die Django automatisch erstellt
        # wenn kein related_name im ForeignKey des Comment-Modells definiert ist.
        return obj.comment_set.count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
