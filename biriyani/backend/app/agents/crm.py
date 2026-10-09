import re
from typing import Any
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.models.user import User
from app.tools.crm_tools import (
    tool_get_user_statistics,
    tool_search_users,
    tool_get_user_details,
    tool_get_user_activity,
    tool_get_recent_users,
    tool_get_inactive_users,
    tool_get_subscription_statistics,
    tool_get_users_by_subscription,
    tool_get_payment_statistics,
    tool_get_admin_analytics,
    tool_customer_summary,
    tool_get_pipeline_summary,
)


class CRMAgent:
    """
    CRM Agent for Admin Users:
    - Parses natural-language questions regarding application users, subscriptions, payments, and activity.
    - Executes controlled backend tools over real application users.
    - Fills state["crm_results"] with structured JSON data.
    """

    def run(self, state: AgentState, db: Session, current_user: User) -> dict[str, Any]:
        query = state.get("user_query", "").strip()
        q_lower = query.lower()

        tool_used = ""
        results = {}

        # 1. Inactive users query
        if "haven't logged in" in q_lower or "inactive user" in q_lower or "not logged in" in q_lower:
            days = 30
            m_days = re.search(r"(\d+)\s*day", q_lower)
            if m_days:
                days = int(m_days.group(1))
            tool_used = "get_inactive_users"
            results = tool_get_inactive_users(db, current_user, days=days)

        # 2. Subscription specific queries (e.g. Pro plan, Premium plan, Free plan)
        elif "pro plan" in q_lower or "pro subscription" in q_lower or "on pro" in q_lower:
            tool_used = "get_users_by_subscription"
            results = tool_get_users_by_subscription(db, current_user, plan="PRO")
        elif "premium plan" in q_lower or "premium subscription" in q_lower or "on premium" in q_lower:
            tool_used = "get_users_by_subscription"
            results = tool_get_users_by_subscription(db, current_user, plan="PREMIUM")
        elif "free plan" in q_lower or "free subscription" in q_lower or "free user" in q_lower:
            tool_used = "get_users_by_subscription"
            results = tool_get_users_by_subscription(db, current_user, plan="FREE")

        # 3. Subscription statistics overall
        elif "subscription" in q_lower and ("stat" in q_lower or "breakdown" in q_lower or "distribution" in q_lower):
            tool_used = "get_subscription_statistics"
            results = tool_get_subscription_statistics(db, current_user)

        # 4. Payment queries
        elif "payment" in q_lower or "revenue" in q_lower or "paid" in q_lower:
            tool_used = "get_payment_statistics"
            results = tool_get_payment_statistics(db, current_user)

        # 5. Recent or new users
        elif "recent user" in q_lower or "new user" in q_lower or "joined" in q_lower or "registered" in q_lower:
            tool_used = "get_recent_users"
            results = tool_get_recent_users(db, current_user, limit=10)

        # 6. Specific user detail search (e.g. "Tell me about Rahul", "Find user Priya")
        elif any(k in q_lower for k in ["about user", "user details", "about rahul", "about priya", "find user"]):
            # Extract target username
            m_name = re.search(r'(?:user|about|find)\s+([A-Za-z0-9\s]+?)(?:\s+details|\?|\.|$)', query, re.IGNORECASE)
            name_query = m_name.group(1).strip() if m_name else query
            tool_used = "get_user_details"
            results = tool_get_user_details(db, current_user, user_id=name_query)

        # 7. Active users or top users
        elif "active user" in q_lower or "top user" in q_lower or "most active" in q_lower:
            tool_used = "search_users"
            results = tool_search_users(db, current_user, query="", limit=5)

        # 8. User Activity summary
        elif "activity" in q_lower or "user activity" in q_lower:
            tool_used = "get_admin_analytics"
            results = tool_get_admin_analytics(db, current_user)

        # 9. General User / Admin Analytics Summary
        else:
            tool_used = "get_admin_analytics"
            results = tool_get_admin_analytics(db, current_user)

        return {
            "crm_tool": tool_used,
            "crm_results": results,
            "agent_trace": state.get("agent_trace", []) + [{
                "agent": "CRM Agent",
                "action": f"Executed tool `{tool_used}`",
            }],
        }
