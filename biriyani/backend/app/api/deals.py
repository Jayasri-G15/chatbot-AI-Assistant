from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.crm_service import CRMService

router = APIRouter(prefix="/api/v1/deals", tags=["Deals"])


@router.get("")
def list_deals(
    status: Optional[str] = Query(None, description="Filter by deal status (open, won, lost)"),
    min_value: Optional[float] = Query(None, ge=0.0),
    max_value: Optional[float] = Query(None, ge=0.0),
    owner_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = CRMService.search_deals(
        db=db,
        current_user=current_user,
        status=status,
        min_value=min_value,
        max_value=max_value,
        owner_id=owner_id,
        customer_id=customer_id,
        page=page,
        limit=limit,
    )
    return {"success": True, "data": data}


@router.get("/summary")
def get_pipeline_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = CRMService.get_pipeline_summary(db=db, current_user=current_user)
    return {"success": True, "data": summary}
