from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from board_app.models import Board, BoardMembership
from task_app.models import Comment, Task

# Muss zu GUEST_LOGIN in frontend/shared/js/config.js passen.
DEMO_EMAIL = "kevin@kovacsi.de"
DEMO_PASSWORD = "asdasdasd"
DEMO_FULLNAME = "Kevin Kovacsi"

DEMO_BOARD_TITLE = "Demo Board"

DEMO_TASKS = [
    {
        "title": "Projektstruktur aufsetzen",
        "description": "Django-Projekt mit board_app, task_app und user_auth_app anlegen.",
        "status": "done",
        "priority": "low",
        "due_in_days": -3,
    },
    {
        "title": "Token-Login implementieren",
        "description": "Registration und Login über DRF-TokenAuthentication bereitstellen.",
        "status": "done",
        "priority": "medium",
        "due_in_days": -1,
    },
    {
        "title": "REST-API dokumentieren",
        "description": "Alle Endpoints mit Beispiel-Requests im README beschreiben.",
        "status": "review",
        "priority": "high",
        "due_in_days": 2,
    },
    {
        "title": "Drag & Drop testen",
        "description": "Tasks zwischen den Spalten verschieben und Statuswechsel prüfen.",
        "status": "in-progress",
        "priority": "high",
        "due_in_days": 4,
    },
    {
        "title": "Dashboard-Statistiken bauen",
        "description": "Task-Zähler und nächste Deadline auf dem Dashboard anzeigen.",
        "status": "in-progress",
        "priority": "medium",
        "due_in_days": 7,
    },
    {
        "title": "Deployment vorbereiten",
        "description": "Docker-Setup mit PostgreSQL und Nginx für den Hetzner-Server bauen.",
        "status": "to-do",
        "priority": "high",
        "due_in_days": 10,
    },
    {
        "title": "Feedback einarbeiten",
        "description": "Rückmeldungen aus dem Code-Review sichten und umsetzen.",
        "status": "to-do",
        "priority": "low",
        "due_in_days": 14,
    },
]

DEMO_COMMENTS = {
    "REST-API dokumentieren": [
        "Die Auth-Endpoints sind schon beschrieben, Boards fehlen noch.",
        "Denk an ein Beispiel für den Token-Header!",
    ],
}


class Command(BaseCommand):
    help = "Erstellt den Demo-User (Guest-Login) mit Board, Tasks und Comments. Idempotent."

    def handle(self, *args, **options):
        demo_user, created = User.objects.get_or_create(
            username=DEMO_EMAIL,
            defaults={"email": DEMO_EMAIL, "first_name": DEMO_FULLNAME},
        )
        if created:
            demo_user.set_password(DEMO_PASSWORD)
            demo_user.save()
            self.stdout.write(f"Demo-User angelegt: {DEMO_EMAIL}")

        board, board_created = Board.objects.get_or_create(
            owner=demo_user, title=DEMO_BOARD_TITLE
        )
        # Ohne Membership filtert BoardsList.get_queryset() das Board weg.
        BoardMembership.objects.get_or_create(
            user=demo_user, board=board, defaults={"role": "owner"}
        )
        if board_created:
            self.stdout.write(f"Board angelegt: {DEMO_BOARD_TITLE}")

        today = date.today()
        tasks_created = 0
        for entry in DEMO_TASKS:
            _, task_created = Task.objects.get_or_create(
                board=board,
                title=entry["title"],
                defaults={
                    "description": entry["description"],
                    "status": entry["status"],
                    "priority": entry["priority"],
                    "due_date": today + timedelta(days=entry["due_in_days"]),
                    "assignee": demo_user,
                    "reviewer": demo_user,
                    "creator": demo_user,
                },
            )
            tasks_created += task_created

        comments_created = 0
        for task_title, contents in DEMO_COMMENTS.items():
            task = Task.objects.filter(board=board, title=task_title).first()
            if not task:
                continue
            for content in contents:
                _, comment_created = Comment.objects.get_or_create(
                    task=task, user=demo_user, content=content
                )
                comments_created += comment_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo-Daten bereit ({tasks_created} Tasks, "
                f"{comments_created} Comments neu angelegt)."
            )
        )
