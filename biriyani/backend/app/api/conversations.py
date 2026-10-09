import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.crm_user import UserActivity
from app.schemas.conversation import ConversationOut, ConversationUpdate
from app.services import conversation_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def _get_or_404(db: Session, conversation_id: str, current_user: User):
    conversation = conversation_service.get_conversation(db, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found"}},
        )
    return conversation


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = conversation_service.create_conversation(db)
    conv.user_id = current_user.id
    current_user.last_active_at = datetime.now(timezone.utc)
    db.add(UserActivity(
        user_id=current_user.id,
        activity_type="CHAT_STARTED",
        metadata_json=json.dumps({"conversation_id": conv.id}),
        timestamp=datetime.now(timezone.utc),
    ))
    db.commit()
    db.refresh(conv)
    return conv


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(conversation_service.Conversation).filter(
        conversation_service.Conversation.user_id == current_user.id
    ).order_by(conversation_service.Conversation.updated_at.desc()).all()


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_or_404(db, conversation_id, current_user)


@router.patch("/{conversation_id}", response_model=ConversationOut)
def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _get_or_404(db, conversation_id, current_user)
    if payload.title is not None:
        conversation = conversation_service.update_conversation_title(db, conversation, payload.title)
    return conversation


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _get_or_404(db, conversation_id, current_user)
    conversation_service.delete_conversation(db, conversation)

