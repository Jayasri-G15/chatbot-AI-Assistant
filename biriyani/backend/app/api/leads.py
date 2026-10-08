from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.crm_service import CRMService

router = APIRouter(prefix="/api/v1/leads", tags=["Leads"])


@router.get("")
def list_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = CRMService.get_leads(
        db=db,
        current_user=current_user,
        status=status,
        source=source,
        page=page,
        limit=limit,
    )
    return {"success": True, "data": data}
