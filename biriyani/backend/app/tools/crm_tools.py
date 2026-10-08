from datetime import datetime
from typing import Optional, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.crm_service import CRMService


def tool_search_customer(
    db: Session,
    current_user: User,
    name: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    query: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search customer records by name, email, or company.
    """
    search_term = query or name or email or company or ""
    return CRMService.search_customers(db, current_user, search=search_term, page=1, limit=20)


def tool_get_customer_details(
    db: Session,
    current_user: User,
    customer_id: str,
) -> dict[str, Any]:
    """
    Fetch comprehensive customer profile including contacts, deals, and recent activities.
    """
    if not customer_id or not customer_id.strip():
        return {"error": "Invalid customer_id provided."}

    res = CRMService.get_customer_details(db, current_user, customer_id.strip())
    if not res:
        return {"error": f"Customer '{customer_id}' not found in CRM database."}
    return res


def tool_get_customer_deals(
    db: Session,
    current_user: User,
    customer_id: str,
    status: Optional[str] = None,
) -> dict[str, Any]:
    """
    Get all deals associated with a specific customer.
    """
    if not customer_id or not customer_id.strip():
        return {"error": "Invalid customer_id provided."}

    # Resolve customer ID or name
    details = CRMService.get_customer_details(db, current_user, customer_id.strip())
    if not details:
        return {"error": f"Customer '{customer_id}' not found."}

    cid = details["customer"]["id"]
    return CRMService.search_deals(db, current_user, customer_id=cid, status=status)


def tool_get_top_customers(
    db: Session,
    current_user: User,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Retrieve top customers ranked by open deal value.
    """
    validated_limit = min(max(1, limit), 50)
    customers = CRMService.get_top_customers(db, current_user, limit=validated_limit)
    return {"top_customers": customers, "count": len(customers)}


def tool_get_recent_activities(
    db: Session,
    current_user: User,
    customer_id: Optional[str] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Retrieve recent activity history (calls, meetings, emails, notes).
    """
    validated_limit = min(max(1, limit), 50)

    cid = None
    if customer_id and customer_id.strip():
        details = CRMService.get_customer_details(db, current_user, customer_id.strip())
        if details:
            cid = details["customer"]["id"]

    activities = CRMService.get_recent_activities(
        db, current_user, customer_id=cid, limit=validated_limit
    )
    return {"activities": activities, "count": len(activities)}


def tool_search_deals(
    db: Session,
    current_user: User,
    status: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    close_date_from: Optional[str] = None,
    close_date_to: Optional[str] = None,
    owner_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search and filter deals by status, minimum/maximum deal value, close dates, or owner.
    """
    dt_from = None
    dt_to = None
    if close_date_from:
        try:
            dt_from = datetime.fromisoformat(close_date_from)
        except Exception:
            pass
    if close_date_to:
        try:
            dt_to = datetime.fromisoformat(close_date_to)
        except Exception:
            pass

    return CRMService.search_deals(
        db,
        current_user,
        status=status,
        min_value=min_value,
        max_value=max_value,
        close_date_from=dt_from,
        close_date_to=dt_to,
        owner_id=owner_id,
        limit=20,
    )


def tool_customer_summary(
    db: Session,
    current_user: User,
    customer_id: str,
) -> dict[str, Any]:
    """
    Generates structured facts for a customer suitable for AI summarization.
    """
    details = CRMService.get_customer_details(db, current_user, customer_id)
    if not details:
        return {"error": f"Customer '{customer_id}' not found."}

    cust = details["customer"]
    deals = details["deals"]
    activities = details["activities"]
    contacts = details["contacts"]

    open_deals = [d for d in deals if d["status"] == "open"]
    total_open_val = sum(d["value"] for d in open_deals)
    won_deals = [d for d in deals if d["status"] == "won"]
    total_won_val = sum(d["value"] for d in won_deals)

    return {
        "customer_id": cust["id"],
        "name": cust["name"],
        "company": cust["company"],
        "email": cust["email"],
        "phone": cust["phone"],
        "total_contacts": len(contacts),
        "total_deals": len(deals),
        "open_deals_count": len(open_deals),
        "total_open_deal_value": total_open_val,
        "total_won_deal_value": total_won_val,
        "recent_activities_count": len(activities),
        "latest_activity": activities[0] if activities else None,
        "contacts": contacts,
        "open_deals": open_deals,
        "recent_activities": activities[:5],
    }


def tool_get_pipeline_summary(
    db: Session,
    current_user: User,
) -> dict[str, Any]:
    """
    Retrieves aggregated pipeline overview (total pipeline value, count of open/won deals, top customers).
    """
    return CRMService.get_pipeline_summary(db, current_user)
