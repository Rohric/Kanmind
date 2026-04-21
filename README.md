Hier ist deine README vollständig und sauber ins Englische übersetzt:

---

# Kanmind Backend

This is the Django REST Framework backend for **Kanmind**. It manages the database and provides the API for authentication, boards, and tasks.

## 📋 Prerequisites

Make sure the following are installed on your system:

* Python 3.10+ (or newer)
* Git

## 🚀 Setup & Installation

Follow these steps to set up and start the project locally:

### 1. Clone the repository

Open your terminal and clone the repository:

```bash
git clone https://github.com/Rohric/Kanmind
cd Kanmind/backend
```

### 2. Create & activate a virtual environment

It is highly recommended to use a virtual environment (`venv`) to isolate project dependencies.

**Windows:**

```bash
python -m venv env
env\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

Once the virtual environment is activated (usually indicated by `(env)` in the terminal), install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

The project uses SQLite3 by default. Create the database and required tables with:

```bash
python manage.py migrate
```

### 5. Create an admin account (optional)

To access the built-in Django admin panel, create a superuser:

```bash
python manage.py createsuperuser
```

Follow the instructions in the terminal (username, email, password).

### 6. Start the development server

Start the local server:

```bash
python manage.py runserver
```

The backend is now running! You can access the admin panel at:
`http://127.0.0.1:8000/admin/`

## 📡 API Endpoints

The REST API provides the following main routes (endpoints):

* **Authentication / User:** `/api/` (token-based authentication)
* **Boards:** `/api/boards/`
* **Tasks:** `/api/tasks/`
* **API Auth UI:** `/api-auth/`

## 📖 Detailed API Endpoints & Payloads

Here is a detailed list of routes and the required JSON bodies for requests (e.g., `POST`, `PUT`). All endpoints (except registration and login) require an authentication token in the header (`Authorization: Token <token>`).

### Authentication & Users (`/api/auth/`)

* **`POST registration/`** (Register)

  ```json
  {
    "username": "maxmustermann",
    "email": "max@example.com",
    "password": "SuperSecretPassword123",
    "repeated_password": "SuperSecretPassword123"
  }
  ```

* **`POST login/`** (Login)

  ```json
  {
    "username": "maxmustermann",
    "password": "SuperSecretPassword123"
  }
  ```

  *Returns the authentication token.*

* **`POST logout/`** (Logout)
  Requires only the token in the header, no body needed. The token is deleted on the server.

* **`GET profiles/` & `GET profiles/<int:pk>/`**
  Retrieves all or a specific user profile.

* **`GET users/` & `GET users/<int:pk>/`**
  Retrieves general account data (e.g., ID, username) of registered users.

---

### Boards (`/api/boards/`)

* **`GET /` & `POST /`** (List / create boards)
  To create a new board, provide a title and optionally a list of user IDs as members:

  ```json
  {
    "title": "My Project Board",
    "members":
  }
  ```

* **`GET /<int:pk>/`** (Board details)
  Returns details about the board, its members, and all included tasks.

* **`PUT /<int:pk>/` & `PATCH /<int:pk>/`** (Update board)

  ```json
  {
    "title": "New Project Name",
    "members":
  }
  ```

* **`DELETE /<int:pk>/`** (Delete board)
  Deletes the board (only allowed for the board owner).

---

### Tasks & Comments (`/api/tasks/`)

* **`GET /` & `POST /`** (List / create tasks)
  To create a task:

  ```json
  {
    "board": 1,
    "title": "Set up database",
    "description": "Configure PostgreSQL database",
    "status": "to-do",
    "priority": "high",
    "assignee_id": 2,
    "reviewer_id": 3,
    "due_date": "2026-05-01"
  }
  ```

* **`GET /<int:pk>/`, `PUT`, `PATCH`, `DELETE`**
  Retrieve and modify a specific task (e.g., update status).

* **`GET /<int:task_id>/comments/` & `POST`** (Task comments)

  ```json
  {
    "content": "I set up the database this morning!"
  }
  ```

* **`GET /<int:task_id>/comments/<int:pk>/`, `PUT`, `PATCH`, `DELETE`**
  Edit or delete a specific comment.

* **`GET /assigned-to-me/`**
  Lists all tasks where the logged-in user is the `assignee`.

* **`GET /reviewing/`**
  Lists all tasks where the logged-in user is the `reviewer`.

---

## 🛡️ Detailed Permission System

The backend enforces strict permission checks (in views and serializers) to ensure users only access data intended for them:

### 1. Boards

* Any logged-in user can create a board.
* The creator is automatically added as a **member** and assigned the role **owner**.
* The owner can add or remove other users as members using their IDs.

### 2. Tasks

* Only **board members** can create or edit tasks within a board.
* When assigning an `assignee` or `reviewer`, the API ensures that these users are also members of the respective board.
* **Delete:** Only the *task creator* or the *board owner* can delete a task.

### 3. Comments

* Only **board members** can write comments on tasks within the board.
* **Edit:** You can only edit your *own* comments.
* **Delete:** Only the *comment creator* or the *board owner* can delete a comment.

