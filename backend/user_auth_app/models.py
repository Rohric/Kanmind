from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


class DemoResetState(models.Model):
    """
    Singleton (pk=1): merkt sich, wann der Demo-Account zuletzt
    zurückgesetzt wurde. Wird von der DemoResetMiddleware gelesen und
    vom reset_demo-Command aktualisiert.
    """

    last_reset = models.DateTimeField()

    def __str__(self):
        return f"Letzter Demo-Reset: {self.last_reset:%d.%m.%Y %H:%M}"
