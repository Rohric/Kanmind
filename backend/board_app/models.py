from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BoardMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.board.name})"
