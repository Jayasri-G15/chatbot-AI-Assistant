from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.crm_service import CRMService

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get("")
def list_customers(
    search: Optional[str] = Query(None, description="Search term across name, email, company, phone"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = CRMService.search_customers(
        db=db,
        current_user=current_user,
        search=search,
        page=page,
        limit=limit,
    )
    return {"success": True, "data": data}


@router.get("/top")
def get_top_customers(
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    top = CRMService.get_top_customers(db=db, current_user=current_user, limit=limit)
    return {"success": True, "data": top}


@router.get("/{customer_id}")
def get_customer_details(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    details = CRMService.get_customer_details(
        db=db,
        current_user=current_user,
        customer_id=customer_id,
    )
    if not details:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "CUSTOMER_NOT_FOUND", "message": f"Customer '{customer_id}' not found."}},
        )
    return {"success": True, "data": details}
