from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board
# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=100)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    assignee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assigned_tasks')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review_tasks', null=True, blank=True)

    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
