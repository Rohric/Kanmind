from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from board_app.models import Board
from task_app.models import Comment, Task
from user_auth_app.models import DemoResetState

from .seed_demo import DEMO_EMAIL


class Command(BaseCommand):
    help = (
        "Setzt den Demo-Account (Guest-Login) zurück: löscht alle Demo-Daten "
        "und seedet sie neu. Registrierte User bleiben unangetastet. "
        "Gedacht für einen Cron-Aufruf alle ~20 Minuten."
    )

    def handle(self, *args, **options):
        demo_user = User.objects.filter(username=DEMO_EMAIL).first()

        if demo_user:
            # Cascade räumt Memberships, Tasks und Comments der Demo-Boards mit ab.
            boards_deleted, _ = Board.objects.filter(owner=demo_user).delete()
            # Spuren des Guests außerhalb seiner eigenen Boards.
            tasks_deleted, _ = Task.objects.filter(creator=demo_user).delete()
            comments_deleted, _ = Comment.objects.filter(user=demo_user).delete()
            self.stdout.write(
                f"Demo-Daten gelöscht ({boards_deleted + tasks_deleted + comments_deleted} Objekte)."
            )

        call_command("seed_demo")

        DemoResetState.objects.update_or_create(
            pk=1, defaults={"last_reset": timezone.now()}
        )
        self.stdout.write(self.style.SUCCESS("Demo-Account frisch zurückgesetzt."))
