# Kanmind Backend

Dies ist das Django REST Framework Backend für ein **Kanmind**. Es verwaltet die Datenbank und stellt die API für die Authentifizierung, Boards und Tasks (Aufgaben) bereit.

## 📋 Voraussetzungen

Stelle sicher, dass Folgendes auf deinem System installiert ist:
- [Python 3.10+](https://www.python.org/downloads/) (oder neuer)
- [Git](https://git-scm.com/)

## 🚀 Setup & Installation

Folge diesen Schritten, um das Projekt lokal aufzusetzen und zu starten:

### 1. Repository klonen
Öffne dein Terminal und klone das Repository:
```bash
git clone https://github.com/Rohric/Kanmind
cd Kanmind/backend
```

### 2. Virtuelle Umgebung erstellen & aktivieren
Es wird dringend empfohlen, eine virtuelle Umgebung (`venv`) zu verwenden, um die Abhängigkeiten des Projekts zu isolieren.

**Windows:**
```cmd
python -m venv env
env\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv env
source venv/bin/activate
```

### 3. Abhängigkeiten installieren
Sobald die virtuelle Umgebung aktiviert ist (meist sichtbar an einem `(venv)` im Terminal), installiere die benötigten Pakete:
```bash
pip install -r requirements.txt
```

### 4. Datenbank-Migrationen durchführen
Das Projekt verwendet standardmäßig SQLite3. Erstelle die Datenbank und die benötigten Tabellen mit folgendem Befehl:
```bash
python manage.py migrate
```

### 5. Administrator-Konto erstellen (Optional)
Um Zugriff auf das integrierte Django Admin-Panel zu erhalten, erstelle einen Superuser:
```bash
python manage.py createsuperuser
```
Folge den Anweisungen im Terminal (Benutzername, E-Mail, Passwort).

### 6. Entwicklungsserver starten
Starte den lokalen Server:
```bash
python manage.py runserver
```
Das Backend läuft nun! Du kannst das Admin-Panel im Browser unter `http://127.0.0.1:8000/admin/` aufrufen.

## 📡 API Endpunkte

Folgende Haupt-Routen (Endpunkte) stellt diese REST-API zur Verfügung:

- **Authentifizierung / User:** `/api/auth/` (Token-based Auth)
- **Boards:** `/api/boards/`
- **Aufgaben (Tasks):** `/api/tasks/`
- **API Auth UI:** `/api-auth/`


## 📖 Detaillierte API Endpunkte & Payloads

Hier ist eine genaue Auflistung der Pfade und wie die JSON-Bodys für Anfragen (z.B. `POST`, `PUT`) aussehen müssen. Alle Endpunkte (außer Registrierung und Login) erfordern einen Authentifizierungs-Token im Header (`Authorization: Token <token>`).

### Authentifizierung & Benutzer (`/api/auth/`)

- **`POST registration/`** (Registrierung)
  ```json
  {
    "username": "maxmustermann",
    "email": "max@example.com",
    "password": "SuperSecretPassword123",
    "repeated_password": "SuperSecretPassword123"
  }
  ```
- **`POST login/`** (Login)
  ```json
  {
    "username": "maxmustermann",
    "password": "SuperSecretPassword123"
  }
  ```
  *Gibt den Auth-Token zurück.*
- **`POST logout/`** (Abmelden)
  Erfordert nur den Token im Header, kein Body nötig. Token wird auf dem Server gelöscht.
- **`GET profiles/` & `GET profiles/<int:pk>/`**
  Liest alle bzw. ein spezifisches Benutzerprofil aus.
- **`GET users/` & `GET users/<int:pk>/`**
  Liest allgemeine Account-Daten (wie ID, Username) der registrierten Benutzer aus.

### Boards (`/api/boards/`)

- **`GET /` & `POST /`** (Boards auflisten / erstellen)
  Um ein neues Board zu erstellen, übergib den Titel und optional eine Liste von User-IDs, die Mitglieder sein sollen:
  ```json
  {
    "title": "Mein Projekt-Board",
    "members":
  }
  ```
- **`GET /<int:pk>/`** (Board Details)
  Gibt Details zum Board, den Mitgliedern und allen darin enthaltenen Tasks zurück.
- **`PUT /<int:pk>/` & `PATCH /<int:pk>/`** (Board bearbeiten)
  ```json
  {
    "title": "Neuer Projektname",
    "members":
  }
  ```
- **`DELETE /<int:pk>/`** (Board löschen)
  Löscht das Board (Nur für Board-Owner erlaubt).

### Tasks & Kommentare (`/api/tasks/`)

- **`GET /` & `POST /`** (Tasks auflisten / erstellen)
  Für das Erstellen eines Tasks:
  ```json
  {
    "board": 1,
    "title": "Datenbank aufsetzen",
    "description": "PostgreSQL Datenbank einrichten",
    "status": "to-do",
    "priority": "high",
    "assignee_id": 2,
    "reviewer_id": 3,
    "due_date": "2026-05-01"
  }
  ```
- **`GET /<int:pk>/` , `PUT`, `PATCH`, `DELETE`** (Task Details & Bearbeitung)
  Zum Ändern eines Tasks (z. B. Status-Update).

- **`GET /<int:task_id>/comments/` & `POST`** (Kommentare eines Tasks)
  ```json
  {
    "content": "Ich habe die Datenbank heute morgen aufgesetzt!"
  }
  ```
- **`GET /<int:task_id>/comments/<int:pk>/` , `PUT`, `PATCH`, `DELETE`**
  Einen spezifischen Kommentar bearbeiten oder löschen.

- **`GET /assigned-to-me/`**
  Listet alle Tasks auf, bei denen der eingeloggte Benutzer als `assignee` eingetragen ist.
- **`GET /reviewing/`**
  Listet alle Tasks auf, bei denen der eingeloggte Benutzer als `reviewer` eingetragen ist.

---

## 🛡️ Detaillierte Rechteverteilung (Permissions)

Das Backend stellt durch stricte Überprüfungen (in den Views und Serializern) sicher, dass Benutzer nur auf Daten zugreifen können, die für sie bestimmt sind:

1. **Boards:**
   - Jeder eingeloggte User darf ein Board erstellen.
   - Der Ersteller wird automatisch **Mitglied** und erhält die Rolle **Owner**.
   - Der Owner kann jederzeit andere User über ihre IDs als Mitglieder hinzufügen oder entfernen.

2. **Tasks:**
   - Nur **Mitglieder eines Boards** können darin neue Tasks erstellen oder bestehende bearbeiten.
   - Beim Zuweisen eines `assignee` oder `reviewer` stellt die API sicher, dass auch diese User zwingend Mitglieder des betreffenden Boards sein müssen.
   - **Löschen:** Einen Task können ausschließlich der *Ersteller des Tasks* oder der *Owner des Boards* löschen.

3. **Kommentare:**
   - Nur **Mitglieder eines Boards** können Kommentare zu den Tasks innerhalb des Boards verfassen.
   - **Bearbeiten:** Du kannst ausschließlich deine *eigenen* Kommentare bearbeiten.
   - **Löschen:** Einen Kommentar können ausschließlich der *Ersteller des Kommentars* oder der *Owner des Boards* löschen.
