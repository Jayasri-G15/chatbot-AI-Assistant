from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.crm import Customer
from app.models.crm_user import ApplicationEvent, UserActivity, Subscription


SENSITIVE_KEYS = {
    "password", "password_hash", "jwt", "token", "access_token", "api_key",
    "secret", "cvv", "upi_pin", "bank_password", "credit_card", "extracted_text",
    "full_text", "prompt", "system_prompt"
}


def sanitize_event_metadata(raw_metadata: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Sanitize metadata to enforce strict data minimization and privacy rules."""
    if not raw_metadata:
        return {}

    sanitized = {}
    for key, val in raw_metadata.items():
        k_lower = key.lower().strip()
        if any(s in k_lower for s in SENSITIVE_KEYS):
            continue
        if isinstance(val, str) and len(val) > 500:
            sanitized[key] = val[:497] + "…"
        else:
            sanitized[key] = val

    return sanitized


class ApplicationEventService:
    @staticmethod
    def record_event(
        db: Session,
        event_type: str,
        user_id: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        event_id: Optional[str] = None,
    ) -> ApplicationEvent:
        """
        Record a real application event idempotently and synchronize CRM customer & user activity state.
        """
        eid = event_id or str(uuid.uuid4())

        # 1. Idempotency Check: Prevent duplicate event processing
        existing = db.query(ApplicationEvent).filter_by(event_id=eid).first()
        if existing:
            return existing

        now = datetime.now(timezone.utc)
        sanitized_meta = sanitize_event_metadata(metadata)
        meta_str = json.dumps(sanitized_meta)

        # 2. Create ApplicationEvent
        app_event = ApplicationEvent(
            event_id=eid,
            event_type=event_type,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=meta_str,
            status="PROCESSED",
            created_at=now,
        )
        db.add(app_event)

        # 3. Create UserActivity record (map event_type for backward compatibility)
        act_type_map = {
            "USER_SIGNED_UP": "SIGNUP",
            "USER_LOGGED_IN": "LOGIN",
            "USER_LOGGED_OUT": "LOGOUT",
        }
        activity_type_name = act_type_map.get(event_type, event_type)

        user_activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type_name,
            metadata_json=meta_str,
            timestamp=now,
            created_at=now,
        )
        db.add(user_activity)

        # 4. Synchronize User & Customer CRM State
        user = db.get(User, user_id)
        if user:
            user.last_active_at = now

            if event_type == "USER_SIGNED_UP":
                # Deterministic Customer Synchronization
                customer = db.query(Customer).filter_by(email=user.email).first()
                if not customer:
                    customer = Customer(
                        name=user.name,
                        email=user.email,
                        phone=user.phone or "",
                        company="Individual Account",
                        owner_id=user.id,
                        created_at=now,
                    )
                    db.add(customer)

            elif event_type == "USER_LOGGED_IN":
                user.last_login = now
                user.login_count = (user.login_count or 0) + 1

        db.flush()
        return app_event
