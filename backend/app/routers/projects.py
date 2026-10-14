from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, get_project_or_404, require_project_member, require_project_admin

router = APIRouter(prefix="/projects", tags=["projects"])


def _build_project_out(project: models.Project, db: Session) -> schemas.ProjectOut:
    count = db.query(models.ProjectMembership).filter(
        models.ProjectMembership.project_id == project.id
    ).count()
    out = schemas.ProjectOut.model_validate(project)
    out.member_count = count + 1  # +1 for owner
    return out


@router.get("", response_model=schemas.PaginatedProjects)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List projects where the user is owner or member."""
    from sqlalchemy import select
    member_project_ids_subq = (
        select(models.ProjectMembership.project_id)
        .where(models.ProjectMembership.user_id == current_user.id)
    )
    query = db.query(models.Project).filter(
        (models.Project.owner_id == current_user.id) |
        (models.Project.id.in_(member_project_ids_subq))
    )
    if search:
        query = query.filter(models.Project.name.ilike(f"%{search}%"))

    total = query.count()
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [_build_project_out(p, db) for p in projects]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = models.Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _build_project_out(project, db)


@router.get("/{project_id}", response_model=schemas.ProjectDetailOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_member(project, current_user, db)

    memberships = (
        db.query(models.ProjectMembership, models.User)
        .join(models.User, models.ProjectMembership.user_id == models.User.id)
        .filter(models.ProjectMembership.project_id == project_id)
        .all()
    )
    members = [
        schemas.MemberOut(
            user_id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=m.role,
        )
        for m, u in memberships
    ]
    # Add owner as admin
    owner = db.query(models.User).filter(models.User.id == project.owner_id).first()
    owner_entry = schemas.MemberOut(
        user_id=owner.id, email=owner.email, full_name=owner.full_name, role=models.UserRole.admin
    )
    # Avoid duplicate if owner is also in memberships
    member_ids = {m.user_id for m in members}
    if owner.id not in member_ids:
        members.insert(0, owner_entry)

    out = schemas.ProjectDetailOut.model_validate(project)
    out.member_count = len(members)
    out.members = members
    return out


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(
    project_id: int,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_admin(project, current_user, db)
    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description
    db.commit()
    db.refresh(project)
    return _build_project_out(project, db)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_admin(project, current_user, db)
    db.delete(project)
    db.commit()


@router.post("/{project_id}/members", status_code=201)
def add_member(
    project_id: int,
    payload: schemas.AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_admin(project, current_user, db)

    target = db.query(models.User).filter(models.User.email == payload.user_email).first()
    if not target:
        raise HTTPException(status_code=404, detail="User with that email not found")
    if target.id == project.owner_id:
        raise HTTPException(status_code=400, detail="User is already the project owner")

    existing = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.project_id == project_id,
            models.ProjectMembership.user_id == target.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    membership = models.ProjectMembership(
        project_id=project_id, user_id=target.id, role=payload.role
    )
    db.add(membership)
    db.commit()
    return {"message": f"{target.full_name} added as {payload.role}"}


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = get_project_or_404(project_id, db)
    require_project_admin(project, current_user, db)

    membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.project_id == project_id,
            models.ProjectMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(membership)
    db.commit()
