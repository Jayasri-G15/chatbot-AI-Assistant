from typing import Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.conversation import Conversation
from app.models.document import Document


def tool_get_my_profile(db: Session, current_user: User) -> dict[str, Any]:
    """Retrieve personal account profile details for the authenticated user."""
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "account_status": current_user.account_status,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
    }


def tool_get_my_subscription(db: Session, current_user: User) -> dict[str, Any]:
    """Retrieve active subscription tier and feature limits for the authenticated user."""
    return {
        "user_id": current_user.id,
        "plan": getattr(current_user, "plan", "FREE") or "FREE",
        "status": "ACTIVE",
        "features": [
            "100% User-Isolated Conversations",
            "Document Upload & RAG Retrieval",
            "Multi-Agent AI Assistant",
            "Standard API Rate Limits",
        ],
    }


def tool_get_my_usage(db: Session, current_user: User) -> dict[str, Any]:
    """Retrieve account usage metrics (total conversations and uploaded documents) for current user."""
    conv_count = db.query(Conversation).filter(Conversation.user_id == current_user.id).count()
    doc_count = (
        db.query(Document)
        .join(Conversation, Document.conversation_id == Conversation.id)
        .filter(Conversation.user_id == current_user.id)
        .count()
    )
    return {
        "user_id": current_user.id,
        "total_conversations": conv_count,
        "total_documents": doc_count,
    }
