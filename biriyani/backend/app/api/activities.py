from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.crm_service import CRMService

router = APIRouter(prefix="/api/v1/activities", tags=["Activities"])


@router.get("")
def list_activities(
    customer_id: Optional[str] = Query(None),
    activity_type: Optional[str] = Query(None, alias="type"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activities = CRMService.get_recent_activities(
        db=db,
        current_user=current_user,
        customer_id=customer_id,
        activity_type=activity_type,
        limit=limit,
    )
    return {"success": True, "data": {"items": activities, "count": len(activities)}}
