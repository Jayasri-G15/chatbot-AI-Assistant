from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.conversation import _uuid, _now


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    plan: Mapped[str] = mapped_column(String(50), default="FREE", index=True)  # FREE | PRO | PREMIUM | ENTERPRISE
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)  # ACTIVE | CANCELLED | EXPIRED
    billing_cycle: Mapped[str] = mapped_column(String(50), default="monthly")
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    end_date = mapped_column(DateTime(timezone=True), nullable=True)
    provider_customer_id = mapped_column(String(255), nullable=True)
    provider_subscription_id = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    user = relationship("User", back_populates="subscription")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50), default="stripe")
    provider_customer_id = mapped_column(String(255), nullable=True)
    provider_payment_id = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    status: Mapped[str] = mapped_column(String(50), default="PAID", index=True)  # PAID | PENDING | FAILED | REFUNDED
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user = relationship("User", back_populates="payments")


class UserActivity(Base):
    __tablename__ = "user_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    activity_type: Mapped[str] = mapped_column(String(100), index=True)  # SIGNUP | LOGIN | LOGOUT | CHAT_STARTED | MESSAGE_SENT | DOCUMENT_UPLOADED | SUBSCRIPTION_CHANGED | PAYMENT_COMPLETED
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user = relationship("User", back_populates="activities")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id = mapped_column(String(36), nullable=True, index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(20), default="PROCESSED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    user = relationship("User")

