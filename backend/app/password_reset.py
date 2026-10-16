"""Forgot / reset password using a 6-digit code sent by email.

Flow:
  POST /auth/forgot-password  {email}                       -> generic reply
  POST /auth/reset-password   {email, code, new_password}   -> sets the new password

Security notes:
  * On a deployed server the reply to /forgot-password is identical whether or
    not the email exists, so nobody can use it to find out who has an account.
  * Only a hash of the code is stored. Codes expire after 10 minutes, work once,
    and are locked after 5 wrong attempts.
  * One new code per email per 60 seconds (not enforced in local dev mode).

Local dev mode (so you can test without an email service):
  When ALL of these are true, /forgot-password also returns the code in its reply
  and the page fills it in for you:
     - BREVO_API_KEY is not set
     - the RENDER environment variable is not set (Render always sets it)
     - the database is SQLite
  On a deployed server the code is only ever sent by email.
  Set RESET_DEV_MODE=false to switch dev mode off locally as well.
"""
import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import Session

from app.auth import SECRET_KEY, hash_password
from app.database import Base, get_db
from app.models import User

logger = logging.getLogger("taskflow.reset")

CODE_TTL_MINUTES = 10
RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5


def _now() -> datetime:
    """Naive UTC time, which works the same on SQLite and Postgres."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _dev_mode() -> bool:
    """True only on a developer's own machine, never on a deployed server."""
    return (
        os.getenv("RESET_DEV_MODE", "").strip().lower() != "false"
        and not os.getenv("BREVO_API_KEY")
        and not os.getenv("RENDER")
        and os.getenv("DATABASE_URL", "sqlite").strip().lower().startswith("sqlite")
    )


# --------------------------------------------------------------------------- #
# Table (created automatically by Base.metadata.create_all at startup)
# --------------------------------------------------------------------------- #
class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)


def _hash_code(email: str, code: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(), f"{email}:{code}".encode(), hashlib.sha256
    ).hexdigest()


# --------------------------------------------------------------------------- #
# Email sending (Brevo HTTP API; Render's free tier blocks SMTP ports)
# --------------------------------------------------------------------------- #
def send_reset_email(to_email: str, code: str) -> None:
    api_key = os.getenv("BREVO_API_KEY")
    sender = os.getenv("MAIL_FROM")

    if not api_key or not sender:
        # No email service configured: also print the code in the server terminal.
        print(f"[TaskFlow] reset code for {to_email}: {code}", flush=True)
        if not _dev_mode():
            logger.error(
                "BREVO_API_KEY / MAIL_FROM are not set, so no reset email was sent"
            )
        return

    html = (
        "<div style='font-family:Arial,sans-serif;max-width:420px'>"
        "<h2 style='margin:0 0 12px'>TaskFlow password reset</h2>"
        "<p>Use this code to reset your password:</p>"
        f"<p style='font-size:32px;letter-spacing:6px;font-weight:bold;margin:16px 0'>{code}</p>"
        f"<p>It expires in {CODE_TTL_MINUTES} minutes. "
        "If you didn't ask for this, you can ignore this email.</p>"
        "</div>"
    )
    try:
        resp = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json",
            },
            json={
                "sender": {"name": "TaskFlow", "email": sender},
                "to": [{"email": to_email}],
                "subject": "Your TaskFlow password reset code",
                "htmlContent": html,
            },
            timeout=20,
        )
        if resp.status_code >= 300:
            logger.error("Brevo error %s: %s", resp.status_code, resp.text[:300])
    except Exception:
        logger.exception("Could not send reset email")


# --------------------------------------------------------------------------- #
# Request schemas
# --------------------------------------------------------------------------- #
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @field_validator("code")
    @classmethod
    def code_is_six_digits(cls, v: str) -> str:
        v = v.strip()
        if not (len(v) == 6 and v.isdigit()):
            raise ValueError("Code must be 6 digits")
        return v

    @field_validator("new_password")
    @classmethod
    def password_is_strong_enough(cls, v: str) -> str:
        # Keep this in line with the rule in your register schema.
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a letter and a number")
        return v


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
router = APIRouter(prefix="/auth", tags=["auth"])

GENERIC_REPLY = {
    "message": "If that email is registered, a reset code has been sent. "
    "It may take a minute to arrive, so check your spam folder too."
}


def _find_user(db: Session, email: str):
    return db.query(User).filter(func.lower(User.email) == email).first()


@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = body.email.strip().lower()
    dev = _dev_mode()

    user = _find_user(db, email)
    if not user:
        if dev:
            return {
                **GENERIC_REPLY,
                "dev_note": "Local dev mode: no account with this email exists in "
                "your local database. Register it first, or use an email you "
                "registered locally.",
            }
        return GENERIC_REPLY

    cooldown = 0 if dev else RESEND_COOLDOWN_SECONDS
    latest = (
        db.query(PasswordResetCode)
        .filter(PasswordResetCode.email == email)
        .order_by(PasswordResetCode.created_at.desc())
        .first()
    )
    if cooldown and latest and (_now() - latest.created_at).total_seconds() < cooldown:
        return GENERIC_REPLY

    # Retire any older codes so only the newest one works
    db.query(PasswordResetCode).filter(
        PasswordResetCode.email == email, PasswordResetCode.used.is_(False)
    ).update({"used": True})

    code = f"{secrets.randbelow(1_000_000):06d}"
    db.add(
        PasswordResetCode(
            email=email,
            code_hash=_hash_code(email, code),
            expires_at=_now() + timedelta(minutes=CODE_TTL_MINUTES),
        )
    )
    db.commit()

    # Send in the background so the request returns immediately
    background.add_task(send_reset_email, user.email, code)

    if dev:
        return {**GENERIC_REPLY, "dev_code": code}
    return GENERIC_REPLY


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    invalid = HTTPException(status_code=400, detail="Invalid or expired code")

    record = (
        db.query(PasswordResetCode)
        .filter(PasswordResetCode.email == email, PasswordResetCode.used.is_(False))
        .order_by(PasswordResetCode.created_at.desc())
        .first()
    )
    if not record or record.expires_at < _now() or record.attempts >= MAX_ATTEMPTS:
        raise invalid

    if not hmac.compare_digest(record.code_hash, _hash_code(email, body.code)):
        record.attempts += 1
        db.commit()
        raise invalid

    user = _find_user(db, email)
    if not user:
        raise invalid

    user.hashed_password = hash_password(body.new_password)
    record.used = True
    db.commit()
    return {"message": "Password updated. You can now sign in."}
