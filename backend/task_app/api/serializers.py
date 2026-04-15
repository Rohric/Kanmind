from rest_framework import serializers
from task_app.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['board', 'ttile', 'description',
                  'status', 'priority', 'assignee_id', 'reviewer_id', 'due_date']

    def get_board():
        return

    def set_title():
        return

    def set_description():
        return

    def set_status():
        return

    def set_priority():
        return

    def set_assignee_users():
        return

    def set_review_users():
        return

    def set_due_date():
        return
