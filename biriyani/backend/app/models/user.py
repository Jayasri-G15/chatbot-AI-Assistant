from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.conversation import _uuid, _now


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="USER", index=True)  # "ADMIN" | "USER"
    account_status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)  # "ACTIVE" | "DEACTIVATED"
    last_login = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_active_at = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    # Backwards compatibility relationships for legacy CRM tables
    customers = relationship("Customer", back_populates="owner")
    leads = relationship("Lead", back_populates="owner")
    deals = relationship("Deal", back_populates="owner")
    legacy_activities = relationship("Activity", back_populates="owner")
