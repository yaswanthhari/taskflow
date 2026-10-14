from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.models import UserRole, TaskStatus, TaskPriority


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Projects ────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MemberOut(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: UserRole

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    member_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDetailOut(ProjectOut):
    members: List[MemberOut] = []


class AddMemberRequest(BaseModel):
    user_email: EmailStr
    role: UserRole = UserRole.member


# ─── Tasks ───────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None


class AssigneeOut(BaseModel):
    id: int
    full_name: str
    email: str

    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: Optional[int]
    assignee: Optional[AssigneeOut]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_projects: int
    total_tasks: int
    todo: int
    in_progress: int
    done: int
    overdue: int


# ─── Pagination ──────────────────────────────────────────────────────────────

class PaginatedTasks(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TaskOut]


class PaginatedProjects(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProjectOut]
