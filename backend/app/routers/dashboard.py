from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Collect all project IDs the user has access to
    member_ids = [
        row[0]
        for row in db.query(models.ProjectMembership.project_id)
        .filter(models.ProjectMembership.user_id == current_user.id)
        .all()
    ]
    owned_ids = [
        row[0]
        for row in db.query(models.Project.id)
        .filter(models.Project.owner_id == current_user.id)
        .all()
    ]
    all_project_ids = list(set(member_ids + owned_ids))

    project_count = len(all_project_ids)

    tasks_q = db.query(models.Task).filter(models.Task.project_id.in_(all_project_ids))
    total_tasks = tasks_q.count()
    todo = tasks_q.filter(models.Task.status == models.TaskStatus.todo).count()
    in_progress = tasks_q.filter(models.Task.status == models.TaskStatus.in_progress).count()
    done = tasks_q.filter(models.Task.status == models.TaskStatus.done).count()
    overdue = (
        tasks_q.filter(
            models.Task.due_date < date.today(),
            models.Task.status != models.TaskStatus.done,
        ).count()
    )

    return schemas.DashboardStats(
        total_projects=project_count,
        total_tasks=total_tasks,
        todo=todo,
        in_progress=in_progress,
        done=done,
        overdue=overdue,
    )
