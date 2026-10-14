from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import decode_token
from app import models

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_project_or_404(project_id: int, db: Session) -> models.Project:
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def require_project_member(project: models.Project, user: models.User, db: Session) -> models.ProjectMembership:
    """Ensure user is a member (or owner) of the project."""
    if project.owner_id == user.id:
        # owner always has access — synthesise a membership-like object
        return None
    membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.project_id == project.id,
            models.ProjectMembership.user_id == user.id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    return membership


def require_project_admin(project: models.Project, user: models.User, db: Session) -> None:
    """Ensure user is the project owner or has admin membership."""
    if project.owner_id == user.id:
        return
    membership = (
        db.query(models.ProjectMembership)
        .filter(
            models.ProjectMembership.project_id == project.id,
            models.ProjectMembership.user_id == user.id,
        )
        .first()
    )
    if not membership or membership.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
