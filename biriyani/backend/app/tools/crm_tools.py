from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.crm_service import CRMService
from app.services.crm_user_service import CRMUserService


def tool_get_user_statistics(db: Session, current_user: User) -> dict[str, Any]:
    """
    Retrieve system-wide user statistics (total users, admin vs user count, paid vs free breakdown).
    """
    return CRMUserService.get_admin_analytics(db)


def tool_search_users(
    db: Session,
    current_user: User,
    query: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    plan: Optional[str] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search real registered application users by name, email, role, or subscription plan.
    """
    return CRMUserService.list_admin_users(
        db, search=query, role=role, status=status, plan=plan, page=1, limit=limit
    )


def tool_get_user_details(db: Session, current_user: User, user_id: str) -> dict[str, Any]:
    """
    Fetch comprehensive CRM customer profile for a real registered user.
    """
    if not user_id or not user_id.strip():
        return {"error": "Invalid user_id provided."}

    res = CRMUserService.get_user_crm_profile(db, user_id.strip())
    if not res:
        return {"error": f"User '{user_id}' not found in CRM database."}
    return res


def tool_get_user_activity(
    db: Session, current_user: User, user_id: str, limit: int = 10
) -> dict[str, Any]:
    """
    Get recent activity history (signups, logins, conversations, document uploads) for a specific user.
    """
    res = CRMUserService.get_user_crm_profile(db, user_id)
    if not res:
        return {"error": f"User '{user_id}' not found."}
    return {
        "user_id": res["user"]["id"],
        "user_name": res["user"]["name"],
        "activities": res["recent_activities"][:limit],
    }


def tool_get_recent_users(db: Session, current_user: User, limit: int = 5) -> dict[str, Any]:
    """
    Retrieve newest registered application users.
    """
    res = CRMUserService.list_admin_users(db, page=1, limit=limit)
    return {"recent_users": res["items"], "total": res["total"]}


def tool_get_inactive_users(db: Session, current_user: User, days: int = 30) -> dict[str, Any]:
    """
    Find users who have not logged in within the specified number of days.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    users = (
        db.query(User)
        .filter(or_(User.last_login < cutoff, User.last_login.is_(None)))
        .order_by(User.created_at.desc())
        .limit(20)
        .all()
    )
    inactive = [
        {
            "user_id": u.id,
            "name": u.name,
            "email": u.email,
            "last_login": u.last_login.isoformat() if u.last_login else "Never",
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
    return {"inactive_users": inactive, "days_threshold": days, "count": len(inactive)}


def tool_get_subscription_statistics(db: Session, current_user: User) -> dict[str, Any]:
    """
    Get breakdown of active users by subscription tier (FREE, PRO, PREMIUM, ENTERPRISE).
    """
    analytics = CRMUserService.get_admin_analytics(db)
    subs = CRMUserService.list_subscriptions(db)
    plan_counts = {}
    for s in subs:
        p = s["plan"]
        plan_counts[p] = plan_counts.get(p, 0) + 1

    return {
        "free_users": analytics["free_users"],
        "paid_users": analytics["paid_users"],
        "plan_breakdown": plan_counts,
    }


def tool_get_users_by_subscription(
    db: Session, current_user: User, plan: str
) -> dict[str, Any]:
    """
    List registered users on a specific subscription plan (e.g. PRO, PREMIUM, ENTERPRISE, FREE).
    """
    res = CRMUserService.list_admin_users(db, plan=plan, page=1, limit=20)
    return {"plan": plan, "users": res["items"], "count": res["total"]}


def tool_get_payment_statistics(db: Session, current_user: User) -> dict[str, Any]:
    """
    Get payment revenue metrics and recent payment receipts.
    """
    pmts = CRMUserService.list_payments(db)
    total_rev = sum(p["amount"] for p in pmts if p["status"] == "PAID")
    return {"total_revenue": total_rev, "payments_count": len(pmts), "recent_payments": pmts[:10]}


def tool_get_admin_analytics(db: Session, current_user: User) -> dict[str, Any]:
    """
    Retrieve executive analytics dashboard overview.
    """
    return CRMUserService.get_admin_analytics(db)


# Legacy Customer Tools Compatibility
def tool_search_customer(db: Session, current_user: User, query: Optional[str] = None, **kwargs) -> dict[str, Any]:
    return CRMUserService.list_admin_users(db, search=query, page=1, limit=20)

def tool_get_customer_details(db: Session, current_user: User, customer_id: str) -> dict[str, Any]:
    return CRMUserService.get_user_crm_profile(db, customer_id) or {"error": "User not found"}

def tool_get_top_customers(db: Session, current_user: User, limit: int = 5) -> dict[str, Any]:
    res = CRMUserService.list_admin_users(db, page=1, limit=limit)
    return {"top_customers": res["items"], "count": res["total"]}

def tool_customer_summary(db: Session, current_user: User, customer_id: str) -> dict[str, Any]:
    profile = CRMUserService.get_user_crm_profile(db, customer_id)
    return profile if profile else {"error": "User not found"}

def tool_get_pipeline_summary(db: Session, current_user: User) -> dict[str, Any]:
    return CRMUserService.get_admin_analytics(db)

def tool_get_recent_activities(db: Session, current_user: User, **kwargs) -> dict[str, Any]:
    acts = CRMUserService.list_activities(db, limit=15)
    return {"activities": acts, "count": len(acts)}

def tool_search_deals(db: Session, current_user: User, **kwargs) -> dict[str, Any]:
    pmts = CRMUserService.list_payments(db)
    return {"items": pmts, "total": len(pmts)}

def tool_get_customer_deals(db: Session, current_user: User, customer_id: str, **kwargs) -> dict[str, Any]:
    profile = CRMUserService.get_user_crm_profile(db, customer_id)
    return profile if profile else {"error": "User not found"}
