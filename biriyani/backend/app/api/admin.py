from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import require_admin_user
from app.services.crm_user_service import CRMUserService

from pydantic import BaseModel
from app.agents.crm import CRMAgent
from app.agents.state import AgentState

router = APIRouter(prefix="/api/v1/admin", tags=["Admin CRM"])


class CRMAssistantQueryRequest(BaseModel):
    query: str


@router.get("/users")
def get_admin_users(
    search: Optional[str] = Query(None, description="Search term for name, email, or phone"),
    role: Optional[str] = Query(None, description="Filter by role (ADMIN | USER)"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE | DEACTIVATED)"),
    plan: Optional[str] = Query(None, description="Filter by plan (FREE | PRO | PREMIUM | ENTERPRISE)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    data = CRMUserService.list_admin_users(
        db=db,
        search=search,
        role=role,
        status=status,
        plan=plan,
        page=page,
        limit=limit,
    )
    return {"success": True, "data": data}


@router.get("/users/{user_id}")
def get_user_crm_profile(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    profile = CRMUserService.get_user_crm_profile(db=db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "USER_NOT_FOUND", "message": f"User '{user_id}' not found."}},
        )
    return {"success": True, "data": profile}


@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    analytics = CRMUserService.get_admin_analytics(db=db)
    return {"success": True, "data": analytics}


@router.get("/subscriptions")
def get_admin_subscriptions(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    subs = CRMUserService.list_subscriptions(db=db)
    return {"success": True, "data": {"items": subs, "count": len(subs)}}


@router.get("/payments")
def get_admin_payments(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    pmts = CRMUserService.list_payments(db=db)
    return {"success": True, "data": {"items": pmts, "count": len(pmts)}}


@router.get("/activities")
def get_admin_activities(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    activities = CRMUserService.list_activities(db=db, limit=limit)
    return {"success": True, "data": {"items": activities, "count": len(activities)}}


@router.post("/assistant/query")
def admin_ai_crm_query(
    payload: CRMAssistantQueryRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
):
    """
    Admin-only AI CRM query assistant:
    - Parses natural language CRM questions
    - Executes approved read-only CRM tools
    - Generates grounded answers based strictly on real database results
    """
    query = payload.query.strip()
    q_lower = query.lower()

    # Safety check: Refuse raw SQL injection or database secret retrieval attempts
    forbidden_terms = ["select ", "insert ", "update ", "delete ", "drop ", "password_hash", "jwt", "api_key", "secret"]
    if any(term in q_lower for term in forbidden_terms):
        return {
            "success": True,
            "data": {
                "answer": "Access denied. Raw SQL execution, direct database modification, and retrieval of authentication secrets are strictly prohibited.",
                "crm_tool": "security_refusal",
                "crm_results": {"error": "Prohibited database access or secret request"},
                "source": "Security Guardrail",
                "agent_trace": [{"agent": "Security Guardrail", "action": "Refused prohibited query"}],
            },
        }

    # Execute CRM agent over authorized DB tools
    crm_agent = CRMAgent()
    state: AgentState = {
        "user_query": query,
        "history": [],
        "document_ids": [],
        "crm_tool": "",
        "crm_results": {},
        "agent_trace": [],
    }
    crm_output = crm_agent.run(state, db, admin)
    tool_used = crm_output.get("crm_tool", "get_admin_analytics")
    results = crm_output.get("crm_results", {})

    # Construct clean grounded text summary
    if not results or (isinstance(results, dict) and "error" in results):
        answer = f"No matching CRM data found for: '{query}'."
    elif tool_used == "get_inactive_users":
        count = results.get("count", 0)
        days = results.get("days_threshold", 30)
        answer = f"Found {count} user(s) who have not logged in within the past {days} days."
    elif tool_used == "get_users_by_subscription":
        plan = results.get("plan", "PRO")
        count = results.get("count", 0)
        answer = f"There are currently {count} user(s) on the {plan} plan."
    elif tool_used == "get_subscription_statistics":
        paid = results.get("paid_users", 0)
        free = results.get("free_users", 0)
        answer = f"Subscription breakdown: {paid} paid user(s), {free} free tier user(s)."
    elif tool_used == "get_payment_statistics":
        rev = results.get("total_revenue", 0.0)
        cnt = results.get("payments_count", 0)
        answer = f"Recorded {cnt} payment transaction(s) totaling ₹{rev:,.2f} in revenue."
    elif tool_used == "get_recent_users":
        total = results.get("total", 0)
        answer = f"There are {total} registered user(s) in total. Retrieved the most recent registrations."
    elif tool_used == "get_user_details":
        u_info = results.get("user", {})
        answer = f"Customer Profile for '{u_info.get('name', 'User')}': Email: {u_info.get('email')}, Role: {u_info.get('role')}, Status: {u_info.get('account_status')}."
    else:
        u_cnt = results.get("total_users", 0)
        rev = results.get("total_revenue", 0.0)
        convs = results.get("total_conversations", 0)
        answer = f"CRM Summary: {u_cnt} total user(s), {convs} conversation(s), and total revenue of ₹{rev:,.2f}."

    return {
        "success": True,
        "data": {
            "answer": answer,
            "crm_tool": tool_used,
            "crm_results": results,
            "source": "PostgreSQL CRM Database",
            "agent_trace": crm_output.get("agent_trace", []),
        },
    }

