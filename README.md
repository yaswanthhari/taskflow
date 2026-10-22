# TaskFlow

A project and task management app with user accounts, shared projects, a task board and a dashboard.

**Live demo:** https://taskflow-ashen-tau.vercel.app
**API docs (Swagger):** https://taskflow-7oox.onrender.com/docs

> The backend runs on a free Render instance that sleeps when idle. The first request after a quiet period can take up to a minute to wake it up.

## Features

- Register and sign in with JWT authentication (PBKDF2 password hashing)
- **Forgot password:** a 6-digit code is emailed to the user, valid for 10 minutes and usable once
- Create projects and add members by the email they registered with
- Create, assign and track tasks inside a project
- Dashboard with an overview of your projects and tasks
- Automated tests (pytest) and a GitHub Actions CI workflow

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router, Axios |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic 2 |
| Database | SQLite locally, PostgreSQL in production |
| Auth | PyJWT, PBKDF2 |
| Email | Brevo transactional email API |
| Tests / CI | pytest, GitHub Actions |
| Hosting | Vercel (frontend), Render (backend and database) |

## Project structure

```
taskflow/
  backend/
    app/
      main.py            app setup, CORS, routers
      auth.py            hashing and JWT helpers
      database.py        engine and session (SQLite or Postgres)
      password_reset.py  forgot / reset password endpoints
      ...                models, schemas, routers
    tests/
    .env.example
  frontend/
    src/
      api/client.js      Axios client (reads VITE_API_URL)
      pages/             Login, Register, ForgotPassword, ...
```

## Run locally

Requires Python 3.10+ and Node 18+.

**Backend**

```powershell
cd backend
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

API docs: http://127.0.0.1:8002/docs

**Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. By default the frontend talks to `http://127.0.0.1:8002`.

**Tests**

```powershell
cd backend
pytest
```

### Forgot password when running locally

With no `BREVO_API_KEY` set, SQLite as the database, and no `RENDER` variable, the app runs in a local test mode. The reset code is shown on the page and filled in automatically, so you can try the flow without an email service. This mode never turns on in production.

## Environment variables

**Backend (Render)**

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string. Defaults to local SQLite |
| `SECRET_KEY` | Long random string used to sign tokens and hash reset codes |
| `CORS_ORIGINS` | Comma-separated frontend URLs, for example the Vercel domain |
| `BREVO_API_KEY` | Brevo API key, needed to send reset emails |
| `MAIL_FROM` | Sender address verified in Brevo |

**Frontend (Vercel)**

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Public URL of the backend. Set before the build, and redeploy after changing it |

Never commit real keys. Copy `backend/.env.example` to `backend/.env` for local use.

## Deployment

- **Backend:** Render web service running `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, with a Render PostgreSQL database
- **Frontend:** Vercel project with root directory `frontend`
- Pushing to `main` redeploys both automatically

Render's free tier blocks outbound SMTP, so reset emails are sent through Brevo's HTTPS API.

## Password reset emails

Reset codes are sent by email through Brevo's API from a single sender address. Any user who requests a reset on the live site receives a 6-digit code from that address.

- Codes expire after 10 minutes, work once, and lock after 5 wrong attempts
- One code per email address per minute
- The reply is the same whether or not the email is registered, so the page can't be used to find out who has an account
- The free Brevo plan allows 300 emails per day
- The sender is a personal Gmail address, so messages may land in spam. Authenticating a domain in Brevo would fix that

## Notes

- Free Render PostgreSQL databases expire after 30 days, so recreate or upgrade it when it does.
- SMS reset codes are not implemented, since they need a paid provider.
- Possible improvements: per-IP rate limiting on the reset endpoint, and a custom sender domain.
