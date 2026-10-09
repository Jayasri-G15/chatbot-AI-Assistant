import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.crm_user import Subscription, UserActivity
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

ADMIN_EMAIL = "jayasrijs1501@gmail.com"


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    existing = db.query(User).filter(User.email.ilike(email_clean)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "USER_EXISTS", "message": "An account with this email already exists."}},
        )

    now = datetime.now(timezone.utc)
    # Check if initial admin email
    role = "ADMIN" if email_clean == ADMIN_EMAIL.lower() else "USER"

    user = User(
        name=payload.name.strip(),
        email=email_clean,
        phone=payload.phone.strip() if payload.phone else None,
        password_hash=hash_password(payload.password),
        role=role,
        account_status="ACTIVE",
        last_login=now,
        last_active_at=now,
        login_count=1,
        created_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically initialize Subscription & Activity
    sub = Subscription(user_id=user.id, plan="FREE", status="ACTIVE", start_date=now)
    db.add(sub)
    db.commit()

    # Record real signup event in ApplicationEvent pipeline
    from app.services.event_service import ApplicationEventService
    ApplicationEventService.record_event(
        db,
        event_type="USER_SIGNED_UP",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        metadata={"email": user.email, "role": role},
        event_id=f"signup-{user.id}",
    )
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
        },
    }


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(email_clean)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}},
        )

    # Record real login event
    from app.services.event_service import ApplicationEventService
    ApplicationEventService.record_event(
        db,
        event_type="USER_LOGGED_IN",
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        metadata={"ip": "127.0.0.1"},
    )
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
        },
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.event_service import ApplicationEventService
    ApplicationEventService.record_event(
        db,
        event_type="USER_LOGGED_OUT",
        user_id=current_user.id,
        entity_type="user",
        entity_id=current_user.id,
    )
    db.commit()
    return {"success": True, "message": "Logged out successfully."}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }
