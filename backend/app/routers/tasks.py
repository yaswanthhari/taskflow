from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, get_project_or_404, require_project_member, require_project_admin

router = APIRouter(tags=["tasks"])


@router.get("/projects/{project_id}/tasks", response_model=schemas.PaginatedTasks)
def list_tasks(
    project_id: int,
    status: Optional[models.TaskStatus] = None,
    priority: Optional[models.TaskPriority] = None,
    assignee_id: Optional[int] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|due_date|priority|status|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_member(project, current_user, db)

    query = db.query(models.Task).filter(models.Task.project_id == project_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if assignee_id is not None:
        query = query.filter(models.Task.assignee_id == assignee_id)

    sort_col = getattr(models.Task, sort_by, models.Task.created_at)
    if order == "desc":
        sort_col = sort_col.desc()
    query = query.order_by(sort_col)

    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": tasks}


@router.post("/projects/{project_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(
    project_id: int,
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_member(project, current_user, db)

    if payload.assignee_id:
        # Verify assignee is a project member
        is_owner = project.owner_id == payload.assignee_id
        is_member = (
            db.query(models.ProjectMembership)
            .filter(
                models.ProjectMembership.project_id == project_id,
                models.ProjectMembership.user_id == payload.assignee_id,
            )
            .first()
        )
        if not is_owner and not is_member:
            raise HTTPException(status_code=400, detail="Assignee must be a project member")

    task = models.Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=project_id,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = get_project_or_404(task.project_id, db)
    require_project_member(project, current_user, db)
    return task


@router.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = get_project_or_404(task.project_id, db)
    require_project_member(project, current_user, db)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = date.today()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = get_project_or_404(task.project_id, db)
    require_project_member(project, current_user, db)
    db.delete(task)
    db.commit()
