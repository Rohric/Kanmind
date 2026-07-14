import logging
import time
from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)

# So lange darf der Guest wüten, bevor aufgeräumt wird.
RESET_INTERVAL = timedelta(minutes=20)

# DB-Abfrage höchstens einmal pro Minute statt bei jedem Request.
CHECK_EVERY_SECONDS = 60


class DemoResetMiddleware:
    """
    Setzt den Demo-Account (Guest-Login) automatisch zurück, sobald der
    letzte Reset länger als RESET_INTERVAL her ist.

    Läuft huckepack auf eingehenden Requests statt über einen externen
    Scheduler — funktioniert damit identisch unter runserver, Gunicorn
    und im Docker-Container, ohne Cron. Wenn niemand die Seite besucht,
    gibt es auch nichts aufzuräumen.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._next_check = 0.0

    def __call__(self, request):
        self._maybe_reset()
        return self.get_response(request)

    def _maybe_reset(self):
        now = time.monotonic()
        if now < self._next_check:
            return
        self._next_check = now + CHECK_EVERY_SECONDS

        try:
            self._reset_if_due()
        except Exception:
            # Der Demo-Reset darf niemals echte Requests kaputt machen.
            logger.exception("Demo-Reset fehlgeschlagen")

    def _reset_if_due(self):
        from user_auth_app.models import DemoResetState

        state, created = DemoResetState.objects.get_or_create(
            pk=1, defaults={"last_reset": timezone.now()}
        )
        if created:
            # Erster Start: Demo-Daten anlegen, Intervall beginnt jetzt.
            call_command("seed_demo")
            return

        if timezone.now() - state.last_reset >= RESET_INTERVAL:
            call_command("reset_demo")
