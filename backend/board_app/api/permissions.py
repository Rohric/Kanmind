from rest_framework.permissions import BasePermission
from board_app.models import Board


class IsMemberOrOwner(BasePermission):
    # Standard-Fehlermeldung für 403-Fehler
    message = "Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein."

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        is_board_obj = isinstance(obj, Board)
        board = None
        if is_board_obj:
            board = obj
        elif hasattr(obj, 'board'):  # Handles Task objects
            board = obj.board
        elif hasattr(obj, 'task') and hasattr(obj.task, 'board'):  # Handles Comment objects
            board = obj.task.board

        if not board:
            return False  # Fallback, if no board can be determined

        if is_board_obj and request.method == "DELETE":
            # Spezifische Fehlermeldung, wenn der User nicht der Owner ist beim Löschen
            self.message = "Verboten. Der Benutzer muss der Eigentümer des Boards sein, um es zu löschen."
            return board.memberships.filter(user=request.user, role='owner').exists()

        # Setzt die Nachricht für alle anderen Fälle (GET, PATCH) auf den Standard zurück
        self.message = "Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein."
        return board.memberships.filter(user=request.user).exists()
