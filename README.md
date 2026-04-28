# Kanban Board API

A REST API backend for a Kanban-style project management application, built with Django and Django REST Framework. It supports multi-user boards, task management with priorities and statuses, comments, and token-based authentication.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables & Secret Key](#environment-variables--secret-key)
- [Running the Server](#running-the-server)
- [Authentication & User Workflow](#authentication--user-workflow)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Permissions](#permissions)

---

## Tech Stack

- Python 3.14
- Django 6.0
- Django REST Framework
- SQLite (development)
- Token Authentication (DRF built-in)

---

## Project Structure

```
backend/
├── core/                   # Project settings, root URLs
├── board_app/              # Boards and memberships
│   └── api/                # Serializers, views, permissions, URLs
├── task_app/               # Tasks and comments
│   └── api/
├── user_auth_app/          # Registration, login, user profiles
│   └── api/
├── .env                    # Secret keys & local config (never commit this)
├── .env.template           # Template with placeholder values
└── manage.py
```

---

## Setup & Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd backend
```

**2. Create and activate a virtual environment**
```bash
python -m venv env

# Windows
env\Scripts\activate

# macOS / Linux
source env/bin/activate
```

**3. Install dependencies**
```bash
pip install django djangorestframework python-dotenv
```

**4. Set up your environment file** — see the section below.

**5. Apply migrations**
```bash
python manage.py migrate
```

**6. (Optional) Create a superuser for the Django admin**
```bash
python manage.py createsuperuser
```

---

## Environment Variables & Secret Key

This project uses a `.env` file to keep secrets out of version control. The file is listed in `.gitignore` and must **never** be committed.

**Step 1 — Copy the template**
```bash
cp .env.template .env
```

**Step 2 — Generate a new SECRET_KEY**

Run this command and copy the output:
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Step 3 — Fill in your `.env` file**
```
SECRET_KEY=paste-your-generated-key-here
```

Your `.env.template` should only ever contain a placeholder, never a real key:
```
SECRET_KEY=your-secret-key-here
```

> ⚠️ **Important:** If a real SECRET_KEY was ever accidentally committed to Git, generating a new one is not enough — it still exists in the repository history. You must remove it from the history using `git filter-branch` or the BFG Repo Cleaner, then force-push. Treat the old key as permanently compromised and always generate a fresh one after cleaning the history.

---

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Authentication & User Workflow

This API uses **token-based authentication**. Every protected endpoint requires the token to be sent in the request header:

```
Authorization: Token <your-token-here>
```

### Full Workflow: From Registration to Creating a Task

Here is the complete sequence of steps a new user takes to register, join a board, and create a task.

---

#### 1. Register a new account

**`POST /api/registration/`** — No authentication required.

```json
// Request body
{
  "fullname": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword123",
  "repeated_password": "securepassword123"
}
```

```json
// Response 201
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "fullname": "Jane Doe",
  "email": "jane@example.com",
  "user_id": 3
}
```

Save the `token`. You will need it for every subsequent request.

---

#### 2. Log in (if you already have an account)

**`POST /api/login/`** — No authentication required.

```json
// Request body
{
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

Returns the same response shape as registration, including your token.

---

#### 3. Create a board

**`POST /api/boards/`** — Requires authentication.

The user who creates the board automatically becomes its **owner**. Other users can be added as members by passing their user IDs.

```json
// Request body
{
  "title": "My First Project",
  "members": [3, 5, 7]
}
```

```json
// Response 201
{
  "id": 1,
  "title": "My First Project",
  "owner_id": 3,
  "member_count": 3,
  "ticket_count": 0,
  "tasks_to_do_count": 0,
  "tasks_high_prio_count": 0
}
```

---

#### 4. Find users to add to your board

Before creating a board or task, you may need to look up other users by email.

**`GET /api/email-check/?email=bob@example.com`** — Requires authentication.

```json
// Response 200
{
  "id": 5,
  "email": "bob@example.com",
  "fullname": "Bob Smith"
}
```

---

#### 5. Create a task

**`POST /api/tasks/`** — Requires authentication. The requesting user must be a member of the target board.

`assignee_id` and `reviewer_id` must also be members of the board.

```json
// Request body
{
  "board": 1,
  "title": "Set up CI pipeline",
  "description": "Configure GitHub Actions for automated testing.",
  "status": "to-do",
  "priority": "high",
  "assignee_id": 5,
  "reviewer_id": 7,
  "due_date": "2026-05-15"
}
```

```json
// Response 201
{
  "id": 12,
  "board": 1,
  "board_title": "My First Project",
  "title": "Set up CI pipeline",
  "description": "Configure GitHub Actions for automated testing.",
  "status": "to-do",
  "priority": "high",
  "assignee": { "id": 5, "email": "bob@example.com", "fullname": "Bob Smith" },
  "reviewer": { "id": 7, "email": "alice@example.com", "fullname": "Alice Jones" },
  "due_date": "2026-05-15",
  "comments_count": 0
}
```

---

#### 6. Add a comment to a task

**`POST /api/tasks/12/comments/`** — Requires authentication. User must be a board member.

```json
// Request body
{
  "content": "I'll start on this today."
}
```

---

#### 7. Log out

**`POST /api/logout/`** — Requires authentication. Deletes the token server-side.

After logout, the token is no longer valid and the user must log in again to get a new one.

---

## API Reference

### Auth & Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/registration/` | ❌ | Register a new user |
| POST | `/api/login/` | ❌ | Log in and receive a token |
| POST | `/api/logout/` | ✅ | Delete the current token |
| GET | `/api/email-check/?email=<email>` | ✅ | Look up a user by email |
| GET | `/api/users/` | ✅ | List all users |
| GET/PATCH/DELETE | `/api/users/<id>/` | ✅ | Retrieve or update a user |
| GET | `/api/profiles/` | ✅ | List all user profiles |
| GET/PATCH/DELETE | `/api/profiles/<id>/` | ✅ | Retrieve or update a profile |

### Boards

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/boards/` | ✅ | List boards the user is a member of |
| POST | `/api/boards/` | ✅ | Create a new board |
| GET | `/api/boards/<id>/` | ✅ | Get board details including all tasks |
| PATCH | `/api/boards/<id>/` | ✅ | Update board title or members |
| DELETE | `/api/boards/<id>/` | ✅ Owner only | Delete a board |

### Tasks

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/tasks/` | ✅ | List all tasks on boards the user belongs to |
| POST | `/api/tasks/` | ✅ Member | Create a new task |
| GET | `/api/tasks/<id>/` | ✅ | Get task details |
| PATCH | `/api/tasks/<id>/` | ✅ Member | Update a task |
| DELETE | `/api/tasks/<id>/` | ✅ Creator or Owner | Delete a task |
| GET | `/api/tasks/assigned-to-me/` | ✅ | List tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | ✅ | List tasks where user is the reviewer |

### Comments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/tasks/<task_id>/comments/` | ✅ | List comments for a task |
| POST | `/api/tasks/<task_id>/comments/` | ✅ Member | Post a comment |
| GET | `/api/tasks/<task_id>/comments/<id>/` | ✅ | Get a single comment |
| PATCH | `/api/tasks/<task_id>/comments/<id>/` | ✅ Author | Edit a comment |
| DELETE | `/api/tasks/<task_id>/comments/<id>/` | ✅ Author or Board Owner | Delete a comment |

---

## Data Models

### Task

| Field | Type | Values |
|-------|------|--------|
| `status` | string | `to-do`, `in-progress`, `review`, `done` |
| `priority` | string | `low`, `medium`, `high` |
| `assignee_id` | integer (write) | User ID — must be a board member |
| `reviewer_id` | integer (write) | User ID — must be a board member |
| `due_date` | date | `YYYY-MM-DD` format |

### Board Membership Roles

| Role | Permissions |
|------|-------------|
| `owner` | Full access: update, delete board, delete any task or comment |
| `member` | Create and update tasks, post and edit own comments |


