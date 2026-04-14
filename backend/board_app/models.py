from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title


class BoardMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='memberships')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'board']

    def __str__(self):
        return f"{self.user} - {self.board} ({self.role})"
