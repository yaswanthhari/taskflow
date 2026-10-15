# TaskFlow — Team Project Management System

> A collaborative task and project tracker for small teams — portfolio project for Software Engineer roles.

---

## ✨ Features

- **User authentication** — JWT-based sign-up/sign-in with PBKDF2-SHA256 password hashing
- **Project management** — Create, update, search, and delete projects
- **Role-based access** — Admin and member roles enforced server-side
- **Team membership** — Invite collaborators by email, remove members
- **Task board** — Kanban-style board (To Do / In Progress / Done) per project
- **Task management** — Create, edit, assign, prioritise, and set due dates on tasks
- **Filtering & pagination** — Filter tasks by status, priority, or assignee; paginated API responses
- **Dashboard** — Overview of open, in-progress, done, and overdue tasks across all projects
- **Automated tests** — 24 pytest tests covering auth, projects, tasks, and access control
- **CI** — GitHub Actions runs tests on every push

---

## 🏗 Architecture

```
taskflow/
├── backend/                  # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py           # App entry + CORS
│   │   ├── database.py       # SQLAlchemy engine/session
│   │   ├── models.py         # ORM: User, Project, Membership, Task
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── auth.py           # JWT + PBKDF2 password hashing (pure stdlib)
│   │   ├── dependencies.py   # get_current_user, membership guards
│   │   └── routers/          # auth, projects, tasks, dashboard
│   └── tests/                # pytest test suite (24 tests)
└── frontend/                 # React 18 + Vite
    └── src/
        ├── api/              # Axios client + endpoint helpers
        ├── context/          # AuthContext (JWT + user state)
        ├── pages/            # Login, Register, Dashboard, Projects, ProjectDetail
        └── components/       # Sidebar
```

### Database Schema

| Table | Key Fields |
|---|---|
| `users` | id, email (unique), full_name, hashed_password, role |
| `projects` | id, name, description, owner_id → users |
| `project_memberships` | project_id, user_id, role (unique constraint) |
| `tasks` | id, title, status, priority, project_id, assignee_id, due_date |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+ and pip
- Node.js 18+ and npm

### Backend

```bash
cd backend
cp .env.example .env          # edit SECRET_KEY for production
pip install -r requirements.txt
uvicorn app.main:app --reload
# API running at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:5173
```

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🔌 API Examples

### Register a user
```http
POST /auth/register
Content-Type: application/json

{
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "password": "securepassword"
}
```

### Create a project
```http
POST /projects
Authorization: Bearer <token>

{ "name": "Website Redesign", "description": "Q1 rebrand" }
```

### Create a task
```http
POST /projects/1/tasks
Authorization: Bearer <token>

{
  "title": "Design landing page",
  "priority": "high",
  "status": "in_progress",
  "due_date": "2025-02-28"
}
```

### Get dashboard stats
```http
GET /dashboard
Authorization: Bearer <token>
```

---

## 🔒 Security

- All task/project endpoints require a valid JWT
- Project access verified server-side (not just frontend)
- Admin-only operations (update/delete project, manage members) checked per request
- Passwords hashed with PBKDF2-HMAC-SHA256 (260k iterations, 16-byte random salt)
- No secrets committed — use environment variables via `.env`

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-...` | JWT signing key — **change in production** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | Token lifetime |
| `DATABASE_URL` | `sqlite:///./taskflow.db` | SQLAlchemy DB URL |

For PostgreSQL: `DATABASE_URL=postgresql://user:pass@localhost:5432/taskflow`

---

## 🐳 Docker

```bash
cp backend/.env.example backend/.env
docker-compose up
```

---

## ⚠️ Known Limitations

- No email verification on sign-up
- File attachments not supported
- No real-time updates (polling or WebSockets not implemented)
- SQLite used locally; PostgreSQL recommended for production

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router, Axios |
| Backend | FastAPI, Uvicorn, SQLAlchemy 2.0 |
| Database | SQLite (local) / PostgreSQL (production) |
| Auth | PyJWT, PBKDF2-HMAC-SHA256 |
| Tests | pytest, httpx TestClient |
| CI | GitHub Actions |
| CSS | Vanilla CSS, dark glassmorphism theme |
