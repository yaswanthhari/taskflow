import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, projects, tasks, dashboard
from app import password_reset
# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="Team Project Management API — Portfolio Project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Comma-separated list in the CORS_ORIGINS env var, e.g.
# https://your-app.vercel.app,http://localhost:5173
DEFAULT_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5174,http://localhost:3000"
)
origins = [
    o.strip().rstrip("/")
    for o in os.getenv("CORS_ORIGINS", DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)
app.include_router(password_reset.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "TaskFlow API"}